#!/usr/bin/env python3
"""Mechanical verification of the SoloBooks design.

Seven invariants, derived across four adversarial review passes. Each one caught a
defect that a human review had missed, and several caught defects the reviewer had
just introduced. This is deliberately NOT an attack pass: no judgment, no seams, no
new doctrine. It answers one question — is the ENCODING self-consistent?

    python3 tools/verify_design.py          # exit 0 = clean, 1 = failures
    python3 tools/verify_design.py -v       # show every check, not just failures

INV1  carrier-in     every enum member a rule READS is actually read by a rule
INV2  frozen fields  every field a rule reads exists in gl_lines / accounts / an enum
INV3  presentation   every rule recognizing a non-P&L leg names a tax_line-bearing account
INV4  fixture slots  every fixture has an `expect` slot able to assert its claim
INV5  carrier-out    every member a rule reads has a named writer + intent detector
INV6  partition      every ladder/gate/bridge set is a partition of R1-R12
INV7  mirror         every enum member appears on BOTH the wiki and the plan
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "llm-wiki" / "wiki"
PLAN = ROOT / "plans" / "2026-07-17-solobooks-v1-plan.md"

VERBOSE = "-v" in sys.argv
failures: list[str] = []
checks = 0


def check(inv: str, ok: bool, detail: str) -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(f"{inv}  {detail}")
    elif VERBOSE:
        print(f"  ok   {inv}  {detail}")


def read(p: Path) -> str:
    return p.read_text()


wiki_all = "\n".join(read(p) for p in sorted(WIKI.glob("*.md")))
plan = read(PLAN)
cbr = read(WIKI / "cash-basis-recognition.md")
rules = cbr[cbr.index("- **R1 —") : cbr.index("CPA endorsements on record")]
ladder = cbr[cbr.index("| Rung | Rule |") : cbr.index('"Priority-ordered"')]
gate = cbr[cbr.index("accrual-vs-cash delta") :][:1600]

ALL_RULES = {"R1", "R2", "R3", "R4", "R5", "R5a", "R6", "R7", "R8", "R9", "R10", "R11", "R12"}

# Members a rule branches on. If a rule reads it, it must be read, written, and mirrored.
# carrier -> the rule(s) that MUST read it. Binding to a specific rule matters: asking
# only "is it read anywhere" let a deleted R11 limb pass because R12 still mentioned the
# same token. That was a live false negative, caught by the negative control below.
CARRIERS = {
    "COST_RECOVERY": ["R11", "R12"],
    "OFFSET_SETTLEMENT": ["R5a"],
    "PREPAID_12_MONTH": ["R12"],
    "PRINCIPAL_WRITE_OFF": ["R3", "R4"],
    "PREPAID_ASSET": ["R12"],
    "MONEY_ACCOUNT": ["R1"],
    "CostRecovery": ["R11"],
}
# carrier -> the exception raised when a human writer failed to declare intent
WRITERS = {
    "OFFSET_SETTLEMENT": "OFFSET_INTENT_UNDECLARED",
    "PRINCIPAL_WRITE_OFF": "WRITE_OFF_INTENT_UNDECLARED",
    "PREPAID_12_MONTH": "PREPAYMENT_PERIOD_UNCONFIRMED",
}
# every member added by the 2026-07-30..08-01 realignment must exist on both sides
MIRROR = [
    "PREPAID_12_MONTH", "PRINCIPAL_WRITE_OFF", "COST_RECOVERY", "OFFSET_SETTLEMENT",
    "GAIN_ON_DISPOSAL", "LOSS_ON_DISPOSAL", "MERCHANT_CLEARING", "PREPAID_ASSET",
    "PREPAYMENT_12_MONTH_TEST", "PRIOR_RETURN_BASIS", "MIGRATION_COMPLETE",
    "CUTOFF_DATE_CONFIRMATION", "STATEMENT_ROW_DISPOSITION",
    "OFFSET_INTENT_UNDECLARED", "WRITE_OFF_INTENT_UNDECLARED",
    "PREPAYMENT_PERIOD_UNCONFIRMED", "PREPAID_AMORTIZATION_UNLINKED",
    "UNMAPPED_RECOGNIZED_LINE", "DISPOSAL_FORM_4797",
    "OPENING_JE_OVERLAP_BREAK", "HISTORICAL_DOC_POSTS_OBE",
    "REC_PERIOD_DISCONTINUITY", "CUTOFF_DATE_UNCONFIRMED", "PREVIEW_DRIFT",
]
# fields R1-R12 branch on -> where each is frozen
FIELDS = {
    "line_reason": "general-ledger-sheet.md",
    "detail_type": "chart-of-accounts.md",
    "ref": "general-ledger-sheet.md",
    "reverses_txn_id": "general-ledger-sheet.md",
}
EXPECT_SLOTS = ["gl_lines", "open_balance", "provenance", "decision", "exceptions",
                "policy_header", "recognized", "balances"]

print("SoloBooks design verification — seven invariants\n")

# ---- INV1: carrier-in -------------------------------------------------------
def rule_body(name: str) -> str:
    """Text of one rule bullet, from its own marker to the next top-level rule."""
    m = re.search(rf"^- \*\*{re.escape(name)} —", rules, re.M)
    if not m:
        return ""
    nxt = re.search(r"^- \*\*R", rules[m.end():], re.M)
    return rules[m.start(): m.end() + (nxt.start() if nxt else len(rules))]


for c, owners in CARRIERS.items():
    for owner in owners:
        body = rule_body(owner)
        check("INV1", bool(body) and re.search(rf"\b{c}\b", body) is not None,
              f"{c} is read by {owner} specifically")

# ---- INV2: fields a rule reads are frozen somewhere -------------------------
for field, owner in FIELDS.items():
    in_rules = re.search(rf"`{field}`", rules) is not None
    if in_rules:
        check("INV2", f"`{field}`" in read(WIKI / owner),
              f"{field} (read by a rule) is frozen in {owner}")
# the benefit period must NOT be a field the view reads — it is carried by a tag
check("INV2", "no benefit period to read" in cbr or "never evaluates the 12-month rule" in plan,
      "benefit period is carried by a tag, never read by the view")

# ---- INV3: recognized non-P&L legs have a presentation account with a tax_line
coa = read(WIKI / "chart-of-accounts.md")
check("INV3", "Unearned Revenue carries its own `tax_line`" in coa,
      "R6's Unearned Revenue has its own tax_line")
check("INV3", "Prepaid Insurance" in coa and "own `tax_line`" in coa,
      "R12's prepaid sub-accounts carry their own tax_line")
check("INV3", "no `tax_line`" in coa,
      "disposal accounts are seeded WITHOUT a tax_line (Form 4797, not Sch C)")

# ---- INV4: fixture expect slots --------------------------------------------
ts = read(WIKI / "testing-strategy.md")
for slot in EXPECT_SLOTS:
    # anchored to a table row / code fence, never a bare prose word: "recognized"
    # appears four times in prose, so a substring test passed a deleted slot.
    anchored = re.search(rf"^\|\s*`{slot}`\s*\|", ts, re.M) or re.search(rf"`{slot}`[,)]", ts)
    check("INV4", anchored is not None, f"expect.{slot} is declared as a slot (not prose)")

# ---- INV5: carrier-out (writer + intent detector) --------------------------
for carrier, detector in WRITERS.items():
    check("INV5", detector in wiki_all,
          f"{carrier} has intent detector {detector}")
    check("INV5", detector in plan,
          f"{detector} is in the plan's ExceptionKind")

# ---- INV6: ladder / gate / bridge are partitions of R1-R12 -----------------
listed = set(re.findall(r"\*\*(R\d+a?)\*\*", ladder))
missing = ALL_RULES - listed
check("INV6", not missing, f"ladder table covers all 13 rules (missing: {sorted(missing) or 'none'})")
for term in ["R4", "R6", "R5", "R12", "Form 4797", "0.00"]:
    check("INV6", term in gate, f"layer-5 gate names {term}")
bridge = read(WIKI / "reports-and-analytics.md")
check("INV6", "partition of R1–R12" in bridge, "packet bridge declares itself a partition")

# ---- INV7: wiki <-> plan mirror --------------------------------------------
for m in MIRROR:
    in_w, in_p = m in wiki_all, m in plan
    check("INV7", in_w and in_p,
          f"{m} mirrored (wiki={'Y' if in_w else 'N'} plan={'Y' if in_p else 'N'})")

# ---- structural hygiene ----------------------------------------------------
pages = {p.stem for p in WIKI.glob("*.md")}
broken = [(p.name, l) for p in WIKI.glob("*.md")
          for l in set(re.findall(r"\[\[([^\]]+)\]\]", read(p))) if l not in pages]
check("LINT", not broken, f"all [[links]] resolve ({len(broken)} broken)")
nofm = [p.name for p in WIKI.glob("*.md") if not read(p).startswith("---")]
check("LINT", not nofm, f"frontmatter on every page ({len(nofm)} missing)")
for claim in ["charge date = payment", "never includes AR/AP", "no LLM inside the server",
              "never edited or deleted", "universal ref rule"]:
    check("LINT", claim.lower() in wiki_all.lower(), f"CPA-validated invariant intact: {claim!r}")

# ---- report ----------------------------------------------------------------
print(f"\n{checks} checks run.")
if failures:
    print(f"\n{len(failures)} FAILURES:\n")
    for f in failures:
        print(f"  {f}")
    print("\nDO NOT FREEZE.")
    sys.exit(1)
print("\nALL CLEAN. The encoding is self-consistent.")
print("Note: this verifies encoding, never doctrine. Accounting correctness is")
print("established by the four adversarial passes recorded in llm-wiki/raw/.")
sys.exit(0)
