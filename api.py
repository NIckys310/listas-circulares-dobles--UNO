"""
Actions the web page can ask for. Shared by the local server (server.py)
and by the in-browser Python used on GitHub Pages (Pyodide).
"""

from turn_table import TurnTable

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


def handle(action, body=None):
    """Run an action and return (payload, http_status)."""
    if action == "state":
        return table.to_dict(), 200
    if action not in ACTIONS:
        return {"error": "Acción desconocida."}, 404
    try:
        ACTIONS[action](body or {})
    except ValueError as error:
        return {"error": str(error), **table.to_dict()}, 400
    return table.to_dict(), 200
