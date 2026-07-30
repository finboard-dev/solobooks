---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [skill, agent-behavior, capture, attention]
---

# The Skill

> Ships with the product; written per "The Art of Writing Skills" (`~/Downloads/The Art of Writing Skills.md`) — the founder's standing methodology for all agent skills.

Teaches the agent:

- The accounting vocabulary and the 9 document types ([[document-model]])
- Tool sequences: money arrives → try matching → retainer path → approval ([[pairing-and-matching]], [[approval-flow]])
- When to use `query_books` vs pre-built reports ([[reports-and-analytics]])
- Approval etiquette and the month-close ritual ([[period-locking-month-close]])
- **What NOT to do:** never book transfers as income/expense; never recognize retainers as income; park unknowns in Uncategorized rather than guessing ([[safety-nets]])
- Loan payments split principal (Notes Payable) from interest (Interest Expense) — never expense the whole payment ([[chart-of-accounts]])
- The close ritual and statement-reconciliation flow ([[period-locking-month-close]], [[bank-reconciliation]])
- **How to answer a "why" question.** Every job above is entry-shaped — get the transaction in. Explaining an object that already exists is a separate job with its own retrieval order (below) and its own honesty rule. **(proposed 2026-07-30)**

## Capture discipline — this page owns the capture rule **(proposed 2026-07-30)**

[[financial-object-model]] adds nine context fields someone could ask a human for. Both failure modes are real: if the skill collects them, "I got paid $1,400 from Acme" becomes a five-question interrogation and the product loses the conversational speed the buyer panel actually bought ([[buyer-panel-findings]]); if the skill says nothing, every field ships null forever and the model is decorative. The rule is **free capture is mandatory, paid capture is opt-in**:

| Class | Fields | Skill behavior |
|---|---|---|
| **Free** — the system already knows it | `rule_id`, `policy_version`, `actor`, `origin`, `skill_version`, `approval_mode_at_post` ([[decision-record]], [[policy-set]]) | Written on every decision and posting. Never asked, never optional. **(proposed 2026-07-30)** |
| **Free** — the user already typed it | `memo_verbatim`, `reason_verbatim` | Stored verbatim, never parsed. [[matching-engine]] already does this at zero conversational cost; the precedent generalizes to every document and decision. **(proposed 2026-07-30)** |
| **Paid** — only the human can supply it | `service_period`, `delivered_at`, `evidence[]` ([[evidence]], [[invoice-artifact]]) | Never interrogated at entry. Captured when volunteered, or **retroactively** at the moment the user asks a question that needs it. **(proposed 2026-07-30)** |

- Retroactive capture is the whole trick: "why is INV-0042 still outstanding?" is the correct moment to ask "did you deliver this?" — the user is already holding the object in mind, so the turn is earned. Asking at invoice time is not. **(proposed 2026-07-30)**
- Nulls are phrased per the rendering rule in [[context-assembly]] — "not recorded", never a fact. **(proposed 2026-07-30)**

## Attention policy

The skill IS the attention policy — [[context-assembly]] locates the question classifier client-side on purpose, because the server never sees the question and never runs a model. The skill therefore carries the retrieval order per question type: **(proposed 2026-07-30)**

| The user asks | First call | Then |
|---|---|---|
| "why is this still outstanding?" | `get_object(ref, SETTLEMENT)` | offer the retroactive `delivered_at` question if it is unrecorded **(proposed 2026-07-30)** |
| "why did this recognize then?" | `get_object(ref, TREATMENT)` | cite the recognition rule id and policy version by name **(proposed 2026-07-30)** |
| "who decided this / why this account?" | `get_object(ref, DECISION)` | `get_audit_trail(ref)` when the user wants the full chronology **(proposed 2026-07-30)** |
| "what backs this up?" | `get_object(ref, EVIDENCE)` | `attach_evidence` if the user then references a file **(proposed 2026-07-30)** |

Answer only from what the dossier returned. Where a section comes back empty or is dropped by the section renderer, say so and name it — never fill the gap by inference. **(proposed 2026-07-30)**
