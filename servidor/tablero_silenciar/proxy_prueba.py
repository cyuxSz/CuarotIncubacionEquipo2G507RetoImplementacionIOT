"""Servidor de prueba: sirve para_el_servidor/index.html y pide todo lo demas al tablero real."""
import http.server, urllib.request, pathlib
REAL = "https://xxxx.trycloudflare.com"
AQUI = pathlib.Path(__file__).parent / "para_el_servidor" / "index.html"
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            cuerpo, tipo = AQUI.read_bytes(), "text/html; charset=utf-8"
        else:
            with urllib.request.urlopen(REAL + self.path, timeout=30) as r:
                cuerpo, tipo = r.read(), r.headers.get("Content-Type", "application/octet-stream")
        self.send_response(200); self.send_header("Content-Type", tipo); self.send_header("Content-Length", str(len(cuerpo))); self.end_headers()
        self.wfile.write(cuerpo)
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
