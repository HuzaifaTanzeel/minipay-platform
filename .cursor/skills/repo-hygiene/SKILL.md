---
name: repo-hygiene
description: >-
  Runs a local, offline scan for leaked secrets, missing ignore rules, and
  required scaffold files before push or PR. Use when the user asks to check
  the repo, scan for secrets, verify .gitignore, or confirm the repository is
  safe to push. Does not commit, push, or open pull requests.
---

# Repo hygiene

Deterministic checks. The script is the source of truth; do not “eyeball” a pass.

## When not to use
- Implementing MiniPay features, SQL, Kubernetes manifests, or tests.
- Writing commit messages or opening PRs.

## Run

From the repository root:

```bash
python .cursor/skills/repo-hygiene/scripts/check_repo.py
python .cursor/skills/repo-hygiene/scripts/check_repo.py --json
```

Exit `0` = clean. Exit `1` = findings. Exit `2` = script error.

## How to report
1. List each finding (severity, path, why).
2. Say what was checked even if there are zero findings.
3. Offer a focused fix. Do not apply edits unless the user asks.

## Limits
- This is not a CVE scanner and not `gitleaks` replacement for CI.
- It does not rewrite git history. If a secret was already committed, rotate it and add a follow-up; do not `git filter-branch`.
