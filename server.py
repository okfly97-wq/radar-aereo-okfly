"""
Radar Aereo Brasil - Proxy Server
Deploy-ready for Render.com / Railway / Fly.io
Uses only Python stdlib — zero extra dependencies.
"""
import http.server
import urllib.request
import urllib.parse
import json
import os
import sys
import traceback
import socketserver

# Render.com injects PORT via environment variable
PORT = int(os.environ.get("PORT", 9090))
DIR  = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # ── Proxy OpenSky ────────────────────────────────────────
    def do_GET(self):
        try:
            if self.path.startswith("/api/opensky"):
                self._proxy_opensky()
            else:
                self._serve_file()
        except Exception:
            traceback.print_exc()

    def _proxy_opensky(self):
        parsed = urllib.parse.urlparse(self.path)
        qs     = parsed.query
        target = "https://opensky-network.org/api/states/all"
        if qs:
            target += "?" + qs
        try:
            req = urllib.request.Request(
                target,
                headers={"User-Agent": "RadarBrasil/2.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
            code = 200
        except Exception as ex:
            print("[proxy-error]", ex)
            body = json.dumps({"error": str(ex)}).encode("utf-8")
            code = 502

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _serve_file(self):
        # Serve index.html for any route (single-page app)
        filepath = os.path.join(DIR, "index.html")
        with open(filepath, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def log_message(self, fmt, *args):
        print("  " + (fmt % args))


class ThreadedServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handles multiple simultaneous browser connections."""
    daemon_threads     = True
    allow_reuse_address = True


if __name__ == "__main__":
    os.chdir(DIR)
    # Bind to 0.0.0.0 so Render / Docker can reach it
    server = ThreadedServer(("0.0.0.0", PORT), Handler)
    print("")
    print("  ======================================")
    print("  Radar Aereo Brasil")
    print("  Porta: " + str(PORT))
    print("  ======================================")
    print("")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Encerrado.")
        sys.exit(0)
