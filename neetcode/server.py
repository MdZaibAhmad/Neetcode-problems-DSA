#!/usr/bin/env python3
"""
NeetCode Grind Ledger - local server with JSON file persistence.

    python3 server.py            # http://localhost:8765
    python3 server.py 9000       # pick another port

Every tick and star is POSTed to /api/progress and written straight to
progress.json in this folder. Delete that file to start over; copy it to
another machine to carry your progress with you.
"""

import json
import os
import shutil
import sys
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "progress.json")
MAX_BODY = 2 * 1024 * 1024  # 2 MB is far more than this ever needs

EMPTY = {"app": "neetcode-grind-ledger", "version": 1, "solved": [], "starred": []}


def read_store():
    try:
        with open(STORE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, OSError) as err:
        print("  ! could not read progress.json (%s) - starting empty" % err)
    return dict(EMPTY)


def write_store(data):
    """Write atomically so a crash mid-save cannot truncate your progress."""
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".progress-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        if os.path.exists(STORE):
            shutil.copymode(STORE, tmp)
        os.replace(tmp, STORE)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] in ("/api/progress", "/api/progress/"):
            self._json(200, read_store())
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] not in ("/api/progress", "/api/progress/"):
            self._json(404, {"error": "unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._json(400, {"error": "bad body length"})
            return
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            self._json(400, {"error": "invalid JSON: %s" % err})
            return
        if not isinstance(data, dict):
            self._json(400, {"error": "expected a JSON object"})
            return
        clean = {
            "app": "neetcode-grind-ledger",
            "version": 1,
            "savedAt": data.get("savedAt"),
            "solved": [s for s in data.get("solved", []) if isinstance(s, str)],
            "starred": [s for s in data.get("starred", []) if isinstance(s, str)],
        }
        try:
            write_store(clean)
        except OSError as err:
            self._json(500, {"error": "could not write progress.json: %s" % err})
            return
        self._json(200, {"ok": True,
                         "solved": len(clean["solved"]),
                         "starred": len(clean["starred"])})

    def log_message(self, fmt, *args):
        if self.command == "POST":
            sys.stderr.write("  saved progress.json\n")


def main():
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Port must be a number, e.g. python3 server.py 9000")
            return 1
    if not os.path.exists(os.path.join(HERE, "index.html")):
        print("index.html is missing - keep server.py next to it.")
        return 1
    current = read_store()
    print("NeetCode Grind Ledger")
    print("  open      http://localhost:%d" % port)
    print("  writes    %s" % STORE)
    print("  loaded    %d solved, %d starred"
          % (len(current.get("solved", [])), len(current.get("starred", []))))
    print("  stop      Ctrl+C")
    try:
        HTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped - progress.json is up to date.")
    except OSError as err:
        print("  ! could not start on port %d: %s" % (port, err))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
