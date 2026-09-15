#!/usr/bin/env python3
"""Offline repo hygiene checks. No network. Does not modify the tree."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

SECRET_PATTERNS = [
    (r"(?i)(aws_secret_access_key|private_key|xox[baprs]-)[^\n]{8,}", "credential-shaped token"),
    (r"(?i)-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----", "private key block"),
    (r"(?i)(api[_-]?key|password|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "hard-coded secret assignment"),
]

TRACKED_FORBIDDEN = {".env", "id_rsa", "id_ed25519", "credentials.json"}

REQUIRED_FILES = [
    "LICENSE",
    ".env.example",
    ".gitignore",
    ".editorconfig",
    "AGENTS.md",
    ".cursor/skills/minipay-conventions/SKILL.md",
    ".cursor/skills/incident-rca/SKILL.md",
    ".cursor/skills/repo-hygiene/SKILL.md",
]

GITIGNORE_MUST_CONTAIN = [".env", ".venv/", "__pycache__/"]

TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".json", ".toml", ".env.example", ".txt", ".sql", ".sh"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def git_tracked(root: Path) -> list[str]:
    r = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def gitignore_text(root: Path) -> str:
    p = root / ".gitignore"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def finding(sev: str, kind: str, path: str, why: str) -> dict:
    return {"severity": sev, "kind": kind, "path": path, "why": why}


def scan(root: Path) -> list[dict]:
    findings: list[dict] = []
    tracked = git_tracked(root)
    tracked_set = set(tracked)
    gi = gitignore_text(root)

    for name in TRACKED_FORBIDDEN:
        if name in tracked_set or any(t.endswith("/" + name) or t == name for t in tracked):
            findings.append(finding("high", "tracked-secret-file", name, "This path must never be tracked."))

    for needle in GITIGNORE_MUST_CONTAIN:
        if needle not in gi:
            findings.append(finding("high", "gitignore-missing", ".gitignore", f"Expected ignore entry {needle!r}."))

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            findings.append(finding("medium", "missing-file", rel, "Required scaffold file is missing."))

    for rel in tracked:
        path = root / rel
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".gitignore", ".gitattributes", ".env.example"}:
            if path.stat().st_size > 2_000_000:
                findings.append(finding("low", "large-file", rel, "Tracked file is larger than 2MB."))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if rel.endswith(".example") or rel.endswith(".env.example"):
            continue
        if "CHANGE_ME" in rel:
            continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, text):
                # Allow documentation that talks about secrets without values
                if re.search(r"(?i)CHANGE_ME|example|placeholder|secretKeyRef", text) and "BEGIN" not in text:
                    continue
                findings.append(finding("high", "secret-pattern", rel, f"Matched {label}."))
                break

    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["path"]))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline MiniPay repo hygiene scan.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = repo_root()
    findings = scan(root)
    summary = {
        "root": str(root),
        "findings": findings,
        "summary": {
            "total": len(findings),
            "by_severity": {
                s: sum(1 for f in findings if f["severity"] == s) for s in ("high", "medium", "low")
            },
        },
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        if not findings:
            print(f"OK  {root}  (0 findings)")
        else:
            print(f"FAIL  {len(findings)} finding(s) in {root}")
            for f in findings:
                print(f"  [{f['severity']}] {f['kind']}  {f['path']}: {f['why']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
