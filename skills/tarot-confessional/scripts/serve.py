#!/usr/bin/env python3
"""Local HTTP server for the tarot-confessional skill.

Binds to 0.0.0.0 so the URL is reachable from any interface.
Serves the draw page at / and optionally a reading page at /reading.

Usage
-----
  # Start server with the draw page
  python3 scripts/serve.py --skill-dir <path-to-tarot-confessional>

  # Specify a port (default: auto-select from 17000-17099)
  python3 scripts/serve.py --skill-dir <path> --port 8080

  # Also serve a generated reading page
  python3 scripts/serve.py --skill-dir <path> --reading <path-to-reading.html>

The server prints a JSON line on startup with the URLs, so the Agent
can extract and relay them to the user.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import tempfile
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from build_draw_page import build as build_draw_page


def find_free_port(host: str = "0.0.0.0", preferred: int | None = None) -> int:
    """Return a free TCP port. Try preferred first, then scan 17000-17099."""
    if preferred:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, preferred))
            return preferred
    for port in range(17000, 17100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            continue
    # Long-lived prior sessions can fill the preferred range. Fall back to an
    # OS-assigned ephemeral port so a new draw flow always remains available.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


def get_local_ip() -> str:
    """Get the primary local IP address for display."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


class TarotHandler(SimpleHTTPRequestHandler):
    """Serve assets/ as root, with optional /reading route."""

    reading_html: str | None = None
    draw_html: str | None = None
    serve_dir: str = "."
    last_activity: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.serve_dir, **kwargs)

    def do_GET(self):
        type(self).last_activity = time.monotonic()
        # Route: / or /draw -> draw.html
        if self.path in ("/", "/draw"):
            if self.draw_html:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(self.draw_html.encode("utf-8"))
                return
            self.path = "/draw.html"
        # Route: /reading -> serve reading HTML
        elif self.path == "/reading" and self.reading_html:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.reading_html.encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        # Suppress default logging; Agent doesn't need per-request noise.
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", required=True, type=Path)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--reading", type=Path, default=None,
                        help="Path to a generated reading HTML file to serve at /reading")
    parser.add_argument("--draw", type=Path, default=None,
                        help="Path to a self-contained draw HTML file; defaults to an automatic Base64 build")
    parser.add_argument("--idle-timeout", type=int, default=900,
                        help="Seconds without requests before shutdown; set 0 to disable (default: 900)")
    args = parser.parse_args()
    if args.idle_timeout < 0:
        parser.error("--idle-timeout must be zero or a positive number")

    assets_dir = args.skill_dir / "assets"
    if not assets_dir.is_dir():
        print(f"error: assets directory not found: {assets_dir}", file=sys.stderr)
        return 1

    # Load reading HTML if provided
    reading_content = None
    if args.reading:
        if not args.reading.is_file():
            print(f"error: reading file not found: {args.reading}", file=sys.stderr)
            return 1
        reading_content = args.reading.read_text(encoding="utf-8")

    # Always serve a self-contained draw page so card images do not depend on
    # the caller's current directory, a temporary asset mount, or URL rewriting.
    temp_draw_dir = None
    if args.draw:
        if not args.draw.is_file():
            print(f"error: draw file not found: {args.draw}", file=sys.stderr)
            return 1
        draw_content = args.draw.read_text(encoding="utf-8")
    else:
        temp_draw_dir = tempfile.TemporaryDirectory(prefix="tarot-draw-")
        draw_path = Path(temp_draw_dir.name) / "draw.html"
        try:
            build_draw_page(skill_dir=args.skill_dir, output=draw_path, spread="S3")
            draw_content = draw_path.read_text(encoding="utf-8")
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: could not build self-contained draw page: {exc}", file=sys.stderr)
            temp_draw_dir.cleanup()
            return 1

    port = args.port or find_free_port()
    local_ip = get_local_ip()

    # Store reading content and serve directory on the handler class
    TarotHandler.reading_html = reading_content
    TarotHandler.draw_html = draw_content
    TarotHandler.serve_dir = str(assets_dir)
    TarotHandler.last_activity = time.monotonic()

    server = HTTPServer(("0.0.0.0", port), TarotHandler)
    server.timeout = 1

    urls = {
        "draw": f"http://localhost:{port}/",
        "draw_lan": f"http://{local_ip}:{port}/",
        "idle_timeout_seconds": args.idle_timeout,
    }
    if reading_content:
        urls["reading"] = f"http://localhost:{port}/reading"
        urls["reading_lan"] = f"http://{local_ip}:{port}/reading"

    # Print JSON so Agent can parse
    print(json.dumps(urls, ensure_ascii=False))

    try:
        while True:
            server.handle_request()
            if args.idle_timeout and time.monotonic() - TarotHandler.last_activity >= args.idle_timeout:
                break
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if temp_draw_dir:
            temp_draw_dir.cleanup()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
