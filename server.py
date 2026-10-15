"""
Small web server (Python standard library only, nothing to install).

Run:  python server.py   ->   open http://localhost:5050
"""

import json
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from turn_table import TurnTable

PORT = 5050
STATIC_DIR = Path(__file__).parent / "static"

table = TurnTable()
for demo_name in ("Nicky", "Alex", "Sofía", "Mateo"):
    table.join_player(demo_name)

# action name -> function that receives the JSON body
ACTIONS = {
    "join": lambda body: table.join_player(body.get("name", ""), int(body.get("cards", 7))),
    "join_after": lambda body: table.join_player_after(
        body.get("name", ""), body.get("after", ""), int(body.get("cards", 7))
    ),
    "eliminate": lambda body: table._record(
        f"🚪 {table.eliminate_player(body.get('name', '')).name} abandonó la mesa."
    ),
    "number": lambda body: table.play_number(),
    "reverse": lambda body: table.play_reverse(),
    "skip": lambda body: table.play_skip(),
    "draw_two": lambda body: table.play_draw_two(),
    "draw": lambda body: table.draw_card(),
    "shuffle": lambda body: table.shuffle_seats(),
    "reset": lambda body: table.reset(),
}


class TurnTableHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")  # always serve the latest files
        super().end_headers()

    def _send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/state":
            return self._send_json(table.to_dict())
        return super().do_GET()

    def do_POST(self):
        action = self.path.removeprefix("/api/")
        if action not in ACTIONS:
            return self._send_json({"error": "Acción desconocida."}, 404)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        try:
            ACTIONS[action](body)
        except ValueError as error:
            return self._send_json({"error": str(error), **table.to_dict()}, 400)
        return self._send_json(table.to_dict())

    def log_message(self, *args):
        pass  # keep the console clean


if __name__ == "__main__":
    server = ThreadingHTTPServer(("localhost", PORT), TurnTableHandler)
    url = f"http://localhost:{PORT}"
    print(f"Mesa de turnos UNO corriendo en {url}  (Ctrl+C para salir)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
