# Process-Aware Financial Objects (founder, 2026-07-30)

> Immutable source. Founder architecture position delivered 2026-07-30, framed through one object: the invoice. Directive accompanying it: "review this and use this ideology and update full stack which conflicts with that."

Let's make this concrete with one object: an **invoice**.

The goal is not just to model the invoice. It is to understand everything FinBoard would need to know to explain, retrieve, and act on it correctly.

## Invoice as a process-aware financial object

A traditional accounting system stores something like:

```text
Invoice ID
Customer
Date
Amount
Tax
Due date
Status
Account
```

That is enough to record the transaction.

It is not enough to understand the transaction.

For FinBoard, the invoice should sit inside a wider lifecycle.

```text
Commercial event
      ↓
Contract or order
      ↓
Service delivered
      ↓
Invoice generated
      ↓
Invoice approved
      ↓
Accounting treatment determined
      ↓
Journal entry posted
      ↓
Payment received
      ↓
Payment matched
      ↓
Bank reconciled
      ↓
Revenue reported
```

Each stage creates context.

### 1. Before the invoice exists

The invoice may originate from:

```text
Customer contract
Sales order
Subscription
Usage data
Milestone completion
Manual billing request
```

This matters because the origin affects the accounting treatment.

For example:

* a subscription may require deferred revenue,
* usage billing may depend on consumption records,
* milestone billing may require delivery approval,
* prepaid services may require revenue recognition over time.

So the invoice should know:

```text
originating_event
originating_contract
billing_method
service_period
performance_obligation
```

### 2. When the invoice is created

The system should capture more than the final PDF.

```text
Who created it?
Which system created it?
Was it generated automatically?
Which source data was used?
Which customer and entity does it belong to?
Was the amount overridden?
Was a discount applied?
Was tax calculated automatically?
```

These are not merely audit fields.

They influence future reasoning.

Suppose the user asks:

> Why is this invoice 15% lower than expected?

FinBoard may need to inspect the pricing rule, discount approval, usage source, contract terms, and manual overrides.

### 3. During approval

Approval should be represented as a real workflow, not just a status field.

Instead of:

```text
status = approved
```

FinBoard should understand:

```text
Approval requested from controller
      ↓
Controller requested supporting document
      ↓
Sales uploaded delivery confirmation
      ↓
Controller approved
```

This creates a decision trail.

The important fields may include:

```text
approver
approval_rule
approval_reason
supporting_evidence
exception
decision_timestamp
comments
```

### 4. Accounting treatment

This may be the most important layer.

The invoice itself does not fully determine when revenue should be recognised.

FinBoard may need to evaluate:

```text
Contract terms
Service period
Delivery status
Accounting policy
Entity rules
Revenue recognition method
Materiality threshold
Prior treatment
```

The invoice can therefore connect to a policy decision:

```text
Invoice #1042
      ↓
Revenue recognition assessment
      ↓
Policy: recognise over 12 months
      ↓
Revenue schedule
      ↓
Journal entries
```

Now FinBoard can answer:

> Why did the invoice value differ from recognised revenue?

### 5. Payment and matching

Later, the invoice participates in another workflow.

```text
Invoice issued
      ↓
Payment received
      ↓
Bank transaction imported
      ↓
Payment matched
      ↓
Difference identified
      ↓
Write-off approved
      ↓
Invoice closed
```

The same invoice is now involved in collections, bank matching, reconciliation, and potentially exception handling.

This is why workflow cannot simply be embedded inside the invoice. One object can participate in multiple processes.

## A better object model

The invoice itself could look like:

```text
Invoice
├── Core attributes
├── Commercial context
├── Accounting context
├── Relationships
├── Evidence
├── Current state
├── Derived facts
├── Workflow references
├── Policy references
├── Exceptions
└── Audit history
```

The workflow remains separate:

```text
WorkflowInstance
├── Workflow type
├── Trigger
├── Participants
├── Steps
├── State transitions
├── Rules
├── Exceptions
├── Inputs
├── Outputs
└── Decisions
```

And they connect like this:

```text
Invoice
  participates in
Billing Workflow

Invoice
  participates in
Revenue Recognition Workflow

Invoice
  participates in
Collections Workflow

Invoice
  participates in
Bank Reconciliation Workflow
```

## What retrieval becomes

This architecture changes retrieval completely.

Traditional retrieval:

```text
User query
    ↓
Find matching document
    ↓
Return content
```

FinBoard retrieval:

```text
User query
    ↓
Identify relevant financial object
    ↓
Identify relevant workflow
    ↓
Retrieve connected evidence
    ↓
Retrieve applicable policy
    ↓
Reconstruct decision path
    ↓
Generate explanation
```

That is much closer to how a finance professional investigates an issue.

## Connecting this back to "Attention Is All You Need"

The durable lesson from attention is not merely that every token can look at every other token.

The deeper principle is:

> Relevance is dynamic and depends on the task.

For one question, the most relevant relationship may be:

```text
Invoice → Customer
```

For another:

```text
Invoice → Revenue policy
```

For another:

```text
Invoice → Approval exception
```

For another:

```text
Invoice → Payment → Bank transaction
```

So FinBoard needs a system-level attention mechanism.

The system should decide which objects, workflows, policies, and evidence deserve attention for the current question.

### Example

User asks:

> Why is this invoice still outstanding?

The relevant context is likely:

```text
Invoice status
Due date
Payment history
Collections workflow
Customer communication
Dispute status
Credit note
Bank match
```

User asks:

> Why was revenue deferred?

Now the relevant context changes:

```text
Contract
Service period
Revenue policy
Delivery evidence
Approval history
Revenue schedule
Journal entry
```

Same invoice. Different attention.

## The stronger architectural principle

We can now sharpen the original assumption:

> Accounting software assumes records have fixed meaning. In reality, the meaning of a financial object depends on the workflow, policy, evidence, and question being asked.

That is a strong FinBoard principle.

A possible architecture statement would be:

> **FinBoard does not retrieve records. It reconstructs financial context.**

That may be one of the best ways to describe what makes the system different.
