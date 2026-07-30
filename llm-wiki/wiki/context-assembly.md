---
type: concept
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md]
tags: [retrieval, attention, tools, mcp]
---

# Context Assembly (retrieval as attention)

> Traditional retrieval finds a document and returns its content. SoloBooks must **identify the object → identify the process → retrieve evidence → retrieve the policy in force → reconstruct the decision path → explain**. Today the tool surface is ~35 writes and fixed aggregate reports, and *nothing assembles context for a question*.

## Where attention lives — the load-bearing constraint

Read literally, "the system should decide which objects deserve attention" implies a server-side question classifier. **SoloBooks must not build one.** Two invariants forbid it: the matching engine's *"no LLM inside the server"* ([[matching-engine]]) and *"the MCP tools ARE the API"* ([[product-vision]]) — the server never sees the user's question, only a tool call the client's model already chose. A nondeterministic relevance layer between the user and the canonical views would destroy the design's one trust guarantee.

The adaptation, which is what "headless" means here:

1. **The skill is the attention policy** ([[the-skill]]) — it specifies retrieval order per question type. This is the client-side model doing the attending, which is exactly where the founder source locates it ("relevance is dynamic and depends on the task").
2. **The `lens` parameter is the mechanism** — one tool answers differently for different questions, deterministically. Same object, different attention, no model in the server.

Attention selects *what to retrieve*. It never selects *what is true*: the matching cascade, the recognition rules and every canonical definition stay deterministic and unchanged.

## `get_object(ref, lens)` — the dossier

Returns a financial object as the eleven buckets of [[financial-object-model]], filtered by lens:

| Lens | Assembles | Answers |
|---|---|---|
| `SETTLEMENT` | open balance by ref, due date, payment history, credit notes, bank match, delivery record | "why is this still outstanding?" |
| `TREATMENT` | basis, recognition rule id, policy version in force, tax treatment, service period | "why did this recognize when it did?" |
| `DECISION` | the ordered decision path — categorization, match, approval (with alternatives not taken), amendments | "who decided this, and why?" |
| `EVIDENCE` | linked evidence, statement rows, import rows, conversation refs | "what backs this up?" |
| `FULL` | all of the above | the accountant's dossier |

`get_audit_trail(ref)` returns the ordered trail for one subject. It depends entirely on the audit log's `subject_ref` edge ([[safety-nets]]) — without it a decision path can be grepped but never queried.

## Honest worked examples

The founder source's two questions, answered as v1 actually stands:

**"Why is this invoice still outstanding?"** — `get_object(INV-0042, SETTLEMENT)` returns open balance and its ref-level composition, due date, every partial payment, credit notes, whether the deposit is bank-matched, and **whether the invoice was ever recorded as delivered**. It returns *not recorded* for dispute status and customer communication, because SoloBooks has no collections or dispute workflow and will not have one ([[v1-scope]]). That is a complete answer with a stated boundary — not a guess.

**"Why was revenue deferred?"** — for the one deferral v1 ships, the retainer path, `get_object(…, TREATMENT)` returns the recognition rule ([[cash-basis-recognition]] R6, recognized at receipt), the unearned-revenue balance by customer/project, the drawdown on invoicing, and the policy version. Contract terms, performance obligations and revenue schedules return *not applicable in this scope*, because they are deliberately not built.

**Null is rendered as "not recorded", never as a fact.** A missing `delivered_at` must never read as "not delivered".

## Rendering — a section contract, not a table

The one output mechanism is a token-budget **CSV table** renderer whose truncation levers are all table operations (drop zero rows, collapse depth). A dossier is a nested heterogeneous structure. Reused naively, a year-old invoice with nineteen audit entries blows the budget and the renderer drops the **oldest rows — the original approval**, the single most load-bearing fact in the answer, while a truncation marker at the bottom satisfies "never silently truncate" and the agent explains confidently from a mutilated trail.

Define a **section renderer** alongside the table renderer: a response is an ordered list of named sections, each with a minimum guaranteed allocation and its own explicit `(N earlier entries not shown)` marker. Sections are dropped whole and named, never thinned silently.

## Boundaries

- **Context assembly reads Mongo, never DuckDB** — the ledger/context read-side boundary is owned by [[duckdb-layer]]. The implementation plan's file map has no module for a Mongo read side; it needs one.
- **Tenant isolation stops being structural here.** `get_object(ref)` is the first read surface taking a caller-supplied id, so the sharpened tenant rule in [[mcp-tool-surface]] governs every context read.
- **Read-only, always.** Nothing in this page mutates. Context assembly is a derived read over stores that already exist — it is not a second truth store, and it creates no snapshots ([[point-in-time-balances]]).
