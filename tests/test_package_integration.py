"""Integration tests for the skill packaging workflow."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_skill import package  # noqa: E402


class PackageIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tarot-pkg-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _run(self, version: str) -> tuple[Path, Path, dict]:
        import package_skill as pkg
        original_dist = pkg.DIST
        pkg.DIST = Path(self.tmp) / "dist"
        pkg.DIST.mkdir(parents=True, exist_ok=True)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = package(version)
            self.assertEqual(rc, 0)
            stage = pkg.DIST / "tarot-confessional"
            manifest = json.loads((stage / "manifest.json").read_text(encoding="utf-8"))
            return pkg.DIST, stage, manifest
        finally:
            pkg.DIST = original_dist

    def test_package_creates_required_artifacts(self):
        dist, _stage, _manifest = self._run("0.1.0-test")
        stem = "tarot-confessional-0.1.0-test"
        for artifact in (dist / "tarot-confessional", dist / f"{stem}.tar.gz", dist / f"{stem}.zip", dist / "SHA256SUMS", dist / "MANIFEST.md"):
            with self.subTest(artifact=artifact):
                self.assertTrue(artifact.exists(), f"missing {artifact}")

    def test_manifest_records_version_and_protocol(self):
        _, _stage, manifest = self._run("0.1.0-test")
        self.assertEqual(manifest["name"], "tarot-confessional")
        self.assertEqual(manifest["version"], "0.1.0-test")
        self.assertEqual(manifest["protocol_version"], "TC1")
        self.assertEqual(manifest["deck_size"], 78)
        self.assertEqual(manifest["spreads"], ["F1", "S3", "R3"])

    def test_manifest_lists_every_file_in_stage(self):
        _dist, stage, manifest = self._run("0.1.0-test")
        actual = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}
        self.assertEqual(set(manifest["files"]), actual)
        for required in ("SKILL.md", "assets/draw.html", "assets/reading.html", "scripts/tarot_codec.py", "references/deck.json", "agents/openai.yaml", "manifest.json"):
            self.assertIn(required, actual)

    def test_packaged_draw_page_is_self_contained(self):
        _dist, stage, _manifest = self._run("0.1.0-test")
        html = (stage / "assets" / "draw.html").read_text(encoding="utf-8")
        self.assertIn("data:image/jpeg;base64,", html)
        self.assertNotIn('`images/cards/${card.file}`', html)
        self.assertNotIn('`images/cards-reversed/${card.file}`', html)

    def test_stage_contains_78_upright_card_images(self):
        _dist, stage, _manifest = self._run("0.1.0-test")
        cards_dir = stage / "assets" / "images" / "cards"
        images = sorted(cards_dir.glob("*.jpg"))
        self.assertEqual(len(images), 78)
        self.assertEqual(images[0].name, "00-fool.jpg")
        self.assertEqual(images[-1].name, "77-king-of-pentacles.jpg")

    def test_tarball_extracts_to_matching_layout(self):
        dist, _stage, _manifest = self._run("0.1.0-test")
        extract_dir = Path(self.tmp) / "extract"
        extract_dir.mkdir()
        subprocess.run(
            ["tar", "-xzf", str(dist / "tarot-confessional-0.1.0-test.tar.gz"), "-C", str(extract_dir)],
            check=True,
        )
        extracted = extract_dir / "tarot-confessional"
        self.assertTrue((extracted / "SKILL.md").is_file())
        self.assertTrue((extracted / "scripts" / "tarot_codec.py").is_file())
        self.assertEqual(len(list((extracted / "assets" / "images" / "cards").glob("*.jpg"))), 78)
        self.assertFalse((extracted / "assets" / "images" / "cards-reversed").exists())
        self.assertTrue((extracted / "manifest.json").is_file())

    def test_zip_archive_is_well_formed(self):
        dist, _stage, _manifest = self._run("0.1.0-test")
        zip_path = dist / "tarot-confessional-0.1.0-test.zip"
        with zipfile.ZipFile(zip_path) as zf:
            self.assertIsNone(zf.testzip(), "corrupt entry in zip")
            names = zf.namelist()
        self.assertIn("tarot-confessional/SKILL.md", names)
        self.assertIn("tarot-confessional/manifest.json", names)

    def test_checksums_match_artifact_bytes(self):
        dist, _stage, _manifest = self._run("0.1.0-test")
        sums = (dist / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(sums), 2)
        for line in sums:
            digest, name = line.split("  ")
            actual = hashlib.sha256((dist / name).read_bytes()).hexdigest()
            self.assertEqual(digest, actual, f"checksum mismatch for {name}")

    def test_packaged_codec_round_trips(self):
        dist, _stage, _manifest = self._run("0.1.0-test")
        codec = dist / "tarot-confessional" / "scripts" / "tarot_codec.py"
        deck = dist / "tarot-confessional" / "references" / "deck.json"
        encoded = subprocess.run(
            ["python3", str(codec), "encode", "--spread", "S3", "0U", "18R", "9U"],
            capture_output=True, text=True, check=True,
        )
        code = json.loads(encoded.stdout)["code"]
        decoded = subprocess.run(
            ["python3", str(codec), "decode", code, "--deck", str(deck)],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(decoded.stdout)
        self.assertEqual([c["id"] for c in payload["cards"]], [0, 18, 9])
        self.assertEqual(payload["cards"][1]["orientation"], "reversed")

    def test_required_files_exist_for_distribution(self):
        from package_skill import expected_layout
        missing = expected_layout(ROOT / "skills" / "tarot-confessional")
        self.assertEqual(missing, [], f"distribution prerequisites missing: {missing}")


if __name__ == "__main__":
    unittest.main()
