---
name: incident-rca
description: >-
  Structures MiniPay incident post-mortems (RCA). Use when drafting or editing
  investigation/INCIDENT-*-RCA.md, kubernetes-findings.md, or similar
  operational write-ups. Do not invent root causes without evidence. Do not
  use for git commits or pull requests.
---

# Incident RCA

Use this shape. Prefer evidence over narrative. Rejected hypotheses are required.

```markdown
# INCIDENT-00X – <title>

| Field | Value |
|---|---|
| Severity | P1 / P2 |
| Status | Resolved |
| Detected | user report / probe / test |
| Components | api / db / kubernetes |
| Author | |

## 1. Summary
Three lines: what broke, who was affected, what restored service.

## 2. Observations and reproduction
Commands, transaction refs, HTTP status. What worked vs what failed.

## 3. Evidence
Logs (`request_id`), `kubectl describe` / endpoints, `EXPLAIN`, test output.
Link files under `evidence/`. Paste trimmed command output, not screenshots of terminals.

## 4. Hypotheses considered
| # | Hypothesis | How tested | Result |
Include at least one hypothesis that was **rejected**, with the evidence that killed it.

## 5. Root cause
Trigger vs underlying cause. Name the file, line, or config key.

## 6. Immediate corrective action
What restored service in the first minutes.

## 7. Permanent corrective action
The lasting code/config change (commit hash when available).

## 8. Validation
Test added, command rerun, before/after.

## 9. Preventive controls
Detection (alert/probe/test), prevention (lint/review), runbook update.

## 10. Timeline
| T+ | Event |
```

## Rules
- Do not skip the hypotheses table.
- Do not claim a unique constraint on `transaction_ref` as a fix if existing rows already duplicate.
- For Kubernetes incidents, include `kubectl get endpoints` and probe failures, not only “pods were running”.
- Write as a production drill / post-mortem, not as an exam answer.
