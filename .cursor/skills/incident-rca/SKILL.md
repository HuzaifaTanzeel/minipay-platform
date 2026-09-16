---
name: incident-rca
description: >-
  Structures MiniPay incident post-mortems (RCA). Use when drafting or editing
  investigation/INCIDENT-*-RCA.md or kubernetes-findings.md. Do not invent root
  causes without evidence. Do not use for git commits or pull requests.
---

# Incident RCA

Keep it short. Evidence over story. At least one **rejected** hypothesis.

```markdown
# INCIDENT-00X – <title>

| | |
|---|---|
| Severity | P1 / P2 |
| Status | Resolved |
| Components | api / db / kubernetes |
| Author | |

## What happened
Two or three sentences: symptom, who felt it, what we changed.

## How we reproduced it
Commands, refs, status codes. What still worked.

## Evidence
Link files under `evidence/`. Quote only the numbers that matter (e.g. execution time).

## Hypotheses
| Hypothesis | Test | Result |
|---|---|---|
Include one that you **rejected**.

## Cause
Trigger vs underlying cause. Name the object (table, probe, selector).

## Fix
Immediate (if any) and lasting change (`path` / commit when you have it).

## Check
What you re-ran and the after result.

## Prevent
One detection + one prevention (test, index review, probe).
```

Do not treat this as an exam answer. Do not add `UNIQUE(transaction_ref)` if seed already has duplicates.
