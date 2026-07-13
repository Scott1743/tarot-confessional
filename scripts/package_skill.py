#!/usr/bin/env python3
"""Package the tarot-confessional Agent Skill into the dist/ directory.

This produces:
- dist/tarot-confessional/             extracted skill directory (no version in dir name)
- dist/tarot-confessional-<version>.tar.gz  (version in file name)
- dist/tarot-confessional-<version>.zip     (version in file name)
- dist/SHA256SUMS                        checksum manifest
- dist/MANIFEST.md                       human-readable release notes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "tarot-confessional"
DIST = ROOT / "dist"
INTRODUCTION_SOURCE = ROOT / "introduction" / "index.html"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_layout(skill_dir: Path) -> list[str]:
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "assets/draw.html",
        "assets/reading.html",
        "assets/deck-data.js",
        "assets/tarot-codec.js",
        "assets/images/card-back.jpg",
        "assets/images/forest-whisper-bg.jpg",
        "assets/images/eastern-night-bg_001.jpg",
        "assets/images/purple-silk.jpg",
        "assets/images/cards-reversed/00-fool.jpg",
        "scripts/serve.py",
        "scripts/tarot_codec.py",
        "scripts/build_draw_page.py",
        "scripts/build_reading_page.py",
        "references/deck.json",
        "references/draw-code-protocol.md",
        "references/reading-guidance.md",
    ]
    missing = [rel for rel in required if not (skill_dir / rel).is_file()]
    return missing


def build_manifest(version: str, skill_dir: Path, archive_stem: str) -> dict:
    files = sorted(
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file()
    )
    return {
        "name": "tarot-confessional",
        "version": version,
        "skill_md_name": "tarot-confessional",
        "schema_version": "1",
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact_stem": archive_stem,
        "files": files,
        "spreads": ["F1", "S3", "R3"],
        "protocol_version": "TC1",
        "deck_size": 78,
        "python_min": "3.9",
    }


def write_manifest(skill_dir: Path, manifest: dict) -> Path:
    target = skill_dir / "manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def stage_directory(skill_dir: Path, version: str) -> Path:
    stage = DIST / "tarot-confessional"
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(skill_dir, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return stage


def render_introduction_into(stage: Path, version: str) -> Path | None:
    """Render the introduction page with placeholders filled and copy it into the staged skill."""
    if not INTRODUCTION_SOURCE.is_file():
        return None
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib
    renderer = importlib.import_module("render_introduction")
    intro_dst = stage / "introduction.html"
    template = INTRODUCTION_SOURCE.read_text(encoding="utf-8")
    substitutions = renderer.collect_substitutions(SOURCE, version)
    rendered, _ = renderer.render(template, substitutions)
    intro_dst.write_text(rendered, encoding="utf-8")
    return intro_dst


def write_sums(version: str, stage: Path) -> Path:
    sums_path = DIST / "SHA256SUMS"
    archive_stem = f"tarot-confessional-{version}"
    tar_path = DIST / f"{archive_stem}.tar.gz"
    zip_path = DIST / f"{archive_stem}.zip"
    lines = [
        f"{sha256(tar_path)}  {tar_path.relative_to(DIST).as_posix()}",
        f"{sha256(zip_path)}  {zip_path.relative_to(DIST).as_posix()}",
    ]
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


def make_archives(version: str, stage: Path) -> tuple[Path, Path]:
    archive_stem = f"tarot-confessional-{version}"
    tar_path = DIST / f"{archive_stem}.tar.gz"
    zip_path = DIST / f"{archive_stem}.zip"
    if tar_path.exists():
        tar_path.unlink()
    if zip_path.exists():
        zip_path.unlink()
    # Create tar.gz with "tarot-confessional" as the root directory inside
    import subprocess
    subprocess.run(
        ["tar", "-czf", str(tar_path), "-C", str(DIST), "tarot-confessional"],
        check=True,
    )
    # Create zip with "tarot-confessional" as the root directory inside
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                arcname = path.relative_to(DIST).as_posix()
                zf.write(path, arcname)
    return tar_path, zip_path


def write_release_notes(version: str, manifest: dict, sums_path: Path) -> Path:
    archive_stem = manifest["artifact_stem"]
    tar_size = (DIST / f"{archive_stem}.tar.gz").stat().st_size
    zip_size = (DIST / f"{archive_stem}.zip").stat().st_size
    notes = DIST / "MANIFEST.md"
    body = [
        f"# {manifest['name']} {version}",
        "",
        f"- Built at: {manifest['built_at']}",
        f"- Protocol: {manifest['protocol_version']}",
        f"- Deck size: {manifest['deck_size']} cards",
        f"- Spreads: {', '.join(manifest['spreads'])}",
        f"- Files: {len(manifest['files'])}",
        "",
        "## Layout",
        "",
        "```text",
        "tarot-confessional/           # extracted directory (no version in name)",
        "├── SKILL.md",
        "├── manifest.json",
        "├── agents/openai.yaml",
        "├── assets/",
        "│   ├── draw.html",
        "│   ├── reading.html",
        "│   ├── deck-data.js",
        "│   ├── tarot-codec.js",
        "│   └── images/",
        "│       ├── card-back.jpg",
        "│       ├── forest-whisper-bg.jpg",
        "│       ├── eastern-night-bg_001.jpg",
        "│       ├── purple-silk.jpg",
        "│       └── cards/  (78 jpg)",
        "├── references/",
        "│   ├── deck.json",
        "│   ├── draw-code-protocol.md",
        "│   └── reading-guidance.md",
        "└── scripts/",
        "    ├── serve.py",
        "    ├── build_draw_page.py",
        "    ├── build_reading_page.py",
        "    └── tarot_codec.py",
        "```",
        "",
        "## Artifacts",
        "",
        f"- `{archive_stem}.tar.gz` ({tar_size} bytes)  # version in file name",
        f"- `{archive_stem}.zip` ({zip_size} bytes)  # version in file name",
        f"- `SHA256SUMS`",
        "",
        "## CLI decode example",
        "",
        "```bash",
        f"python3 tarot-confessional/scripts/tarot_codec.py decode \"<TC1 code>\" --deck tarot-confessional/references/deck.json",
        "```",
        "",
        "## Verification",
        "",
        "```bash",
        f"shasum -a 256 -c SHA256SUMS   # macOS / Linux",
        "```",
        "",
    ]
    notes.write_text("\n".join(body), encoding="utf-8")
    return notes


def package(version: str) -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    missing = expected_layout(SOURCE)
    if missing:
        print(f"missing required files in {SOURCE}: {missing}", file=sys.stderr)
        return 1
    archive_stem = f"tarot-confessional-{version}"
    stage = stage_directory(SOURCE, version)
    # Ship the draw page as the same self-contained Base64 artifact that the
    # server serves at runtime. A raw template would lose its image siblings
    # when users open or attach the packaged HTML alone.
    from build_draw_page import build as build_draw_page
    build_draw_page(skill_dir=stage, output=stage / "assets" / "draw.html", spread="S3")
    # Render the introduction page against this version so dist copies
    # always carry the correct version, release date, and changelog summary.
    intro_dst = render_introduction_into(stage, version)
    manifest = build_manifest(version, stage, archive_stem)
    manifest["files"].append("manifest.json")
    manifest["files"] = sorted(set(manifest["files"]))
    write_manifest(stage, manifest)
    tar_path, zip_path = make_archives(version, stage)
    sums_path = write_sums(version, stage)
    notes_path = write_release_notes(version, manifest, sums_path)
    print(f"staged:    {stage}")
    print(f"tarball:   {tar_path} ({tar_path.stat().st_size} bytes)")
    print(f"zip:       {zip_path} ({zip_path.stat().st_size} bytes)")
    print(f"checksums: {sums_path}")
    print(f"manifest:  {stage / 'manifest.json'}")
    print(f"notes:     {notes_path}")
    if intro_dst:
        print(f"intro:     {intro_dst}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="0.1.0")
    args = parser.parse_args()
    return package(args.version)


if __name__ == "__main__":
    raise SystemExit(main())
