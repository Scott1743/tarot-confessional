#!/usr/bin/env python3
"""Small, optional bridge to a locally installed Mneme Agent Skill.

This module never writes a bundle.  It only discovers the local skill, runs
bounded search, and invokes Mneme's read-only ``dream`` audit for the reading
server.  The host Agent owns any consented Markdown writes.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ENV_SKILL_DIR = "MNEME_SKILL_DIR"
ENV_BUNDLE = "MNEME_BUNDLE"
MAX_RESULTS = 3


def find_cli(skill_dir: str | Path | None = None) -> Path | None:
    """Return the Mneme skill entry point without inspecting a user bundle."""
    if skill_dir is not None:
        cli = Path(skill_dir).expanduser() / "scripts" / "mneme.py"
        return cli if cli.is_file() else None
    candidates = [os.environ.get(ENV_SKILL_DIR)]
    home = Path.home()
    candidates.extend((home / ".codex" / "skills" / "mneme", home / ".claude" / "skills" / "mneme"))
    for candidate in candidates:
        if not candidate:
            continue
        cli = Path(candidate).expanduser() / "scripts" / "mneme.py"
        if cli.is_file():
            return cli
    return None


def capabilities(skill_dir: str | Path | None = None) -> dict[str, Any]:
    cli = find_cli(skill_dir)
    return {
        "status": "available" if cli else "unavailable",
        "cli": str(cli) if cli else None,
        "bundle_configured": bool(os.environ.get(ENV_BUNDLE)),
    }


def _run(cli: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(cli), *args], text=True, capture_output=True, check=False, timeout=20)


def search(question: str, *, bundle: str | None = None, skill_dir: str | Path | None = None) -> dict[str, Any]:
    """Return at most three Mneme candidates; never read their Markdown."""
    cli = find_cli(skill_dir)
    if not cli:
        return {"status": "unavailable", "candidates": []}
    args = ["search", question.strip(), "--json", "-k", str(MAX_RESULTS)]
    if bundle:
        args.extend(("--bundle", bundle))
    result = _run(cli, args)
    if result.returncode:
        return {"status": "error", "candidates": [], "message": result.stderr.strip() or result.stdout.strip()}
    try:
        payload = json.loads(result.stdout)
        candidates = payload.get("candidates", [])[:MAX_RESULTS]
    except json.JSONDecodeError:
        return {"status": "error", "candidates": [], "message": "Mneme returned invalid JSON"}
    return {"status": "ok", "candidates": candidates}


def dream(*, bundle: str | None = None, skill_dir: str | Path | None = None) -> dict[str, Any]:
    """Run Mneme's read-only dream audit; it intentionally does not persist."""
    cli = find_cli(skill_dir)
    if not cli:
        return {"status": "unavailable", "message": "Mneme is not installed"}
    args = ["dream", "--json"]
    if bundle:
        args.extend(("--bundle", bundle))
    result = _run(cli, args)
    if result.returncode:
        return {"status": "error", "message": result.stderr.strip() or result.stdout.strip()}
    try:
        return {"status": "ok", "report": json.loads(result.stdout)}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Mneme returned invalid JSON"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", default=None)
    parser.add_argument("--bundle", default=os.environ.get(ENV_BUNDLE))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("capabilities")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("question")
    subparsers.add_parser("dream")
    args = parser.parse_args()
    if args.command == "capabilities":
        output = capabilities(args.skill_dir)
    elif args.command == "search":
        output = search(args.question, bundle=args.bundle, skill_dir=args.skill_dir)
    else:
        output = dream(bundle=args.bundle, skill_dir=args.skill_dir)
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["status"] in {"available", "ok", "unavailable"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
