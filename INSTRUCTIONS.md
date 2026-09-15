# Candidate Instructions

## 1. Submission
Create a **public GitHub repository** containing your complete submission and share its URL within 48 hours.

Do not include passwords, tokens, private keys, personal data, employer/client information, or any confidential material in the repository.

Your repository must contain at minimum:

```text
README.md
SETUP.md
ARCHITECTURE.md
AI_USAGE.md
investigation/
sql/
kubernetes/
python/
tests/api/
tests/ui/
evidence/
```

You may improve this structure.

## 2. Technology choices
You may use local VMs, cloud VMs, Docker, Minikube, Kind, K3s or another reasonable Kubernetes environment. For SQL, PostgreSQL or MySQL/MariaDB is acceptable unless your implementation requires another open-source relational database. You may create a minimal API/UI yourself or use a small open-source/demo application, but your repository must make the environment reproducible for the evaluator.

For Rancher, you may deploy Rancher locally or in an environment available to you. If environmental limitations prevent a full Rancher deployment, document the attempt, commands/configuration, blockers, and how you would perform the required operational tasks in Rancher. A working demonstration earns more credit than theoretical documentation.

## 3. AI usage
Use of AI tools is **permitted and encouraged**. You may use ChatGPT, Claude, Codex, GitHub Copilot or other tools.

We assess your ability to use AI productively while retaining engineering ownership. Create `AI_USAGE.md` containing:
- tools used;
- tasks for which you used them;
- 3–5 representative prompts or interaction summaries;
- how you validated generated output; and
- at least one example where you corrected, rejected, or materially improved AI-generated output.

You must be able to explain and modify any part of your submission during a follow-up interview.

## 4. Git expectations
Use Git throughout the exercise. We expect meaningful incremental commits, clear commit messages, sensible `.gitignore`, and a repository that another engineer can clone and run. Do not submit the entire solution as a single final commit.

## 5. Evidence
Prefer reproducible code and commands over screenshots. Screenshots may be used for Rancher/UI evidence. Remove/redact secrets and unrelated personal information.

## 6. Engineering expectations
Treat MiniPay as if it were a client-facing production system. Do not merely make the demo work. Consider health checks, logging, failure modes, configuration, secrets, resource constraints, repeatability, safe SQL, automated tests, and supportability.

## 7. Follow-up interview
Expect a 30–45 minute technical discussion. The evaluator may select any submitted component and ask you to explain, troubleshoot, or modify it live.
