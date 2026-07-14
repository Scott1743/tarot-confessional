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
ENV_CONFIG_DIR = "MNEME_CONFIG_DIR"
MAX_RESULTS = 3


def find_cli(skill_dir: str | Path | None = None, *, home: Path | None = None) -> Path | None:
    """Return the Mneme skill entry point without inspecting a user bundle."""
    if skill_dir is not None:
        cli = Path(skill_dir).expanduser() / "scripts" / "mneme.py"
        return cli if cli.is_file() else None
    candidates = [os.environ.get(ENV_SKILL_DIR)]
    home = Path.home() if home is None else home
    candidates.extend((
        home / ".codex" / "skills" / "mneme",
        home / ".claude" / "skills" / "mneme",
        home / ".workbuddy" / "skills" / "mneme",
        home / ".agents" / "skills" / "mneme",
    ))
    for candidate in candidates:
        if not candidate:
            continue
        cli = Path(candidate).expanduser() / "scripts" / "mneme.py"
        if cli.is_file():
            return cli
    return None


def resolve_bundle(bundle: str | Path | None = None, *, config: str | Path | None = None) -> Path | None:
    """Resolve Mneme's configured bundle without opening bundle content."""
    explicit = bundle or os.environ.get(ENV_BUNDLE)
    if explicit:
        return Path(explicit).expanduser()

    config_path = Path(config).expanduser() if config else Path(
        os.environ.get(ENV_CONFIG_DIR, Path.home() / ".config" / "mneme")
    ).expanduser() / "config.toml"
    if not config_path.is_file():
        return None
    try:
        import tomllib
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return None
    configured = payload.get("bundle_path")
    return Path(configured).expanduser() if isinstance(configured, str) and configured else None


def capabilities(
    skill_dir: str | Path | None = None,
    *,
    bundle: str | Path | None = None,
    config: str | Path | None = None,
) -> dict[str, Any]:
    cli = find_cli(skill_dir)
    bundle_path = resolve_bundle(bundle, config=config)
    return {
        "status": "available" if cli else "unavailable",
        "cli": str(cli) if cli else None,
        "bundle": str(bundle_path) if bundle_path else None,
        "bundle_configured": bundle_path is not None,
        "bundle_available": bool(bundle_path and bundle_path.is_dir()),
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


def _add_runtime_options(parser: argparse.ArgumentParser, *, suppress_defaults: bool = False) -> None:
    default = argparse.SUPPRESS if suppress_defaults else None
    parser.add_argument("--skill-dir", default=default)
    parser.add_argument("--bundle", default=argparse.SUPPRESS if suppress_defaults else os.environ.get(ENV_BUNDLE))
    parser.add_argument("--config", default=default)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _add_runtime_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)
    capabilities_parser = subparsers.add_parser("capabilities")
    _add_runtime_options(capabilities_parser, suppress_defaults=True)
    search_parser = subparsers.add_parser("search")
    _add_runtime_options(search_parser, suppress_defaults=True)
    search_parser.add_argument("question")
    dream_parser = subparsers.add_parser("dream")
    _add_runtime_options(dream_parser, suppress_defaults=True)
    args = parser.parse_args(argv)
    if args.command == "capabilities":
        output = capabilities(args.skill_dir, bundle=args.bundle, config=args.config)
    elif args.command == "search":
        bundle = resolve_bundle(args.bundle, config=args.config)
        output = search(args.question, bundle=str(bundle) if bundle else None, skill_dir=args.skill_dir)
    else:
        bundle = resolve_bundle(args.bundle, config=args.config)
        output = dream(bundle=str(bundle) if bundle else None, skill_dir=args.skill_dir)
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["status"] in {"available", "ok", "unavailable"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
