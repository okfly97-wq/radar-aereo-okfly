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
import time

# Render.com injects PORT via environment variable
PORT = int(os.environ.get("PORT", 9090))
DIR  = os.path.dirname(os.path.abspath(__file__))

# ── In-Memory Cache (Evita timeouts e bloqueios da OpenSky e ADSB.lol) ──
CACHE      = {"time": 0, "data": b""}
CACHE_ADSB = {"time": 0, "data": b""}


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # ── CORS Preflight (Essencial para GitHub Pages / Nuvemshop) ──
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

    # ── Proxy Rotas ────────────────────────────────────────
    def do_GET(self):
        try:
            if self.path.startswith("/api/adsblol"):
                self._proxy_adsblol()
            elif self.path.startswith("/api/opensky"):
                self._proxy_opensky()
            else:
                self._serve_file()
        except Exception:
            traceback.print_exc()

    def _proxy_adsblol(self):
        global CACHE_ADSB
        # 1. Retorna do cache se tiver menos de 10 segundos
        if CACHE_ADSB["data"] and (time.time() - CACHE_ADSB["time"] < 10):
            body = CACHE_ADSB["data"]
            code = 200
        else:
            try:
                req = urllib.request.Request(
                    "https://api.adsb.lol/v2/lat/-14/lon/-53/dist/2000",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                with urllib.request.urlopen(req, timeout=15) as r:
                    body = r.read()
                code = 200
                CACHE_ADSB["data"] = body
                CACHE_ADSB["time"] = time.time()
            except Exception as ex:
                print("[adsblol-error]", ex)
                if CACHE_ADSB["data"]:
                    print("[adsblol-fallback] Usando cache antigo de ADSB.lol")
                    body = CACHE_ADSB["data"]
                    code = 200
                else:
                    body = json.dumps({"error": str(ex)}).encode("utf-8")
                    code = 502

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _proxy_opensky(self):
        global CACHE
        parsed = urllib.parse.urlparse(self.path)
        qs     = parsed.query
        target = "https://opensky-network.org/api/states/all"
        if qs:
            target += "?" + qs

        # 1. Retorna do cache se tiver menos de 6 segundos
        if CACHE["data"] and (time.time() - CACHE["time"] < 6):
            body = CACHE["data"]
            code = 200
        else:
            try:
                req = urllib.request.Request(
                    target,
                    headers={"User-Agent": "RadarBrasil/3.0 (CORS-Cache-Proxy)"}
                )
                with urllib.request.urlopen(req, timeout=18) as r:
                    body = r.read()
                code = 200
                # Salva no cache
                CACHE["data"] = body
                CACHE["time"] = time.time()
            except Exception as ex:
                print("[proxy-error]", ex)
                # Fallback espetacular: se der erro/timeout mas tivermos cache antigo, entregamos ele!
                if CACHE["data"]:
                    print("[proxy-fallback] Usando cache antigo devido a erro na OpenSky")
                    body = CACHE["data"]
                    code = 200
                else:
                    body = json.dumps({"error": str(ex)}).encode("utf-8")
                    code = 502

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
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
        self.send_header("Access-Control-Allow-Origin", "*")
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
