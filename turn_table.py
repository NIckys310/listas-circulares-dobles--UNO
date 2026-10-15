"""
UNO Turn Table - Circular Doubly Linked List.

Every Player is linked to the one on its left (prev) and on its right (next).
The last player links back to the first one, so the table never "ends":
turns keep rotating forever, in either direction (the UNO "Reverse" card).
"""

import random


class Player:
    """A seat at the table. It is the node of the circular doubly linked list."""

    def __init__(self, name, cards=7):
        self.name = name
        self.cards = cards
        self.next = self  # a lonely player is linked to itself
        self.prev = self

    def to_dict(self):
        return {
            "name": self.name,
            "cards": self.cards,
            "next": self.next.name,
            "prev": self.prev.name,
        }


class TurnTable:
    """Circular doubly linked list of players sitting around a UNO table."""

    MAX_PLAYERS = 10

    def __init__(self):
        self.head = None        # first player who sat down (reference point only)
        self.current = None     # player whose turn it is
        self.size = 0
        self.clockwise = True   # True -> follow .next, False -> follow .prev
        self.winners = []
        self.log = []

    # ------------------------------------------------------------------ helpers
    def is_empty(self):
        return self.head is None

    def _step(self, node):
        """Return the neighbour of `node` in the current play direction."""
        return node.next if self.clockwise else node.prev

    def _record(self, message):
        self.log.insert(0, message)
        del self.log[30:]

    def traverse(self, start=None, clockwise=True):
        """Visit every player exactly once.

        Stop condition: we are back at the starting node (there is no None).
        """
        if self.is_empty():
            return
        start = start or self.head
        node = start
        while True:
            yield node
            node = node.next if clockwise else node.prev
            if node is start:
                break

    def find_player(self, name):
        for player in self.traverse():
            if player.name.lower() == name.lower():
                return player
        return None

    # ---------------------------------------------------------------- insertion
    def join_player(self, name, cards=7):
        """Insert a new player at the end of the circle (between tail and head)."""
        name = name.strip()
        if not name:
            raise ValueError("El nombre no puede estar vacío.")
        if self.size >= self.MAX_PLAYERS:
            raise ValueError(f"La mesa admite máximo {self.MAX_PLAYERS} jugadores.")
        if self.find_player(name):
            raise ValueError(f"Ya existe un jugador llamado {name}.")

        new_player = Player(name, cards)
        if self.is_empty():
            self.head = self.current = new_player
        else:
            tail = self.head.prev
            new_player.next = self.head
            new_player.prev = tail
            tail.next = new_player
            self.head.prev = new_player
        self.size += 1
        self._record(f"🪑 {name} se sentó en la mesa.")
        return new_player

    def join_player_after(self, name, neighbour_name, cards=7):
        """Insert a new player right after (to the right of) an existing one."""
        neighbour = self.find_player(neighbour_name)
        if neighbour is None:
            raise ValueError(f"No existe el jugador {neighbour_name}.")
        if neighbour is self.head.prev:
            return self.join_player(name, cards)  # same as inserting at the end
        if self.size >= self.MAX_PLAYERS:
            raise ValueError(f"La mesa admite máximo {self.MAX_PLAYERS} jugadores.")
        if self.find_player(name):
            raise ValueError(f"Ya existe un jugador llamado {name}.")

        new_player = Player(name.strip(), cards)
        new_player.prev = neighbour
        new_player.next = neighbour.next
        neighbour.next.prev = new_player
        neighbour.next = new_player
        self.size += 1
        self._record(f"🪑 {name} se sentó a la derecha de {neighbour.name}.")
        return new_player

    # ----------------------------------------------------------------- deletion
    def eliminate_player(self, name):
        """Unlink a player. Its neighbours get linked to each other."""
        player = self.find_player(name)
        if player is None:
            raise ValueError(f"No existe el jugador {name}.")

        if self.size == 1:
            self.head = self.current = None
        else:
            player.prev.next = player.next
            player.next.prev = player.prev
            if player is self.head:
                self.head = player.next
            if player is self.current:
                self.current = self._step(player)
        player.next = player.prev = player  # fully detached
        self.size -= 1
        return player

    # -------------------------------------------------------------- game moves
    def _require_game(self):
        if self.size < 2:
            raise ValueError("Se necesitan al menos 2 jugadores para jugar.")

    def next_turn(self):
        self._require_game()
        self.current = self._step(self.current)
        return self.current

    def reverse_direction(self):
        self.clockwise = not self.clockwise
        return self.clockwise

    def skip_turn(self):
        """The next player loses the turn: jump two seats."""
        self._require_game()
        skipped = self._step(self.current)
        self.current = self._step(skipped)
        return skipped

    def _discard(self):
        """Current player drops one card; if they have none left they win."""
        player = self.current
        player.cards -= 1
        if player.cards == 0:
            following = self._step(player)
            self.eliminate_player(player.name)
            self.current = following
            self.winners.append(player.name)
            self._record(f"🏆 ¡{player.name} se quedó sin cartas y gana el puesto {len(self.winners)}!")
            return True
        return False

    def play_number(self):
        self._require_game()
        player = self.current
        self._record(f"🃏 {player.name} jugó una carta numérica.")
        if not self._discard():
            self.next_turn()

    def play_reverse(self):
        self._require_game()
        player = self.current
        self.reverse_direction()
        sense = "horario ↻" if self.clockwise else "antihorario ↺"
        self._record(f"🔄 {player.name} jugó REVERSA. Ahora el sentido es {sense}.")
        if self._discard():
            return
        if self.size == 2:
            return  # with two players Reverse works like Skip: same player again
        self.next_turn()

    def play_skip(self):
        self._require_game()
        player = self.current
        skipped = self._step(player)
        self._record(f"⛔ {player.name} jugó SALTA. {skipped.name} pierde el turno.")
        if self._discard():
            # the winner is gone, so the skipped player is the new current one
            self.current = self._step(self.current) if self.size >= 2 else self.current
            return
        self.skip_turn()

    def play_draw_two(self):
        self._require_game()
        player = self.current
        victim = self._step(player)
        victim.cards += 2
        self._record(f"➕2 {player.name} jugó +2. {victim.name} roba 2 cartas y pierde el turno.")
        if self._discard():
            self.current = self._step(self.current) if self.size >= 2 else self.current
            return
        self.skip_turn()

    def draw_card(self):
        self._require_game()
        player = self.current
        player.cards += 1
        self._record(f"📥 {player.name} robó una carta y pasa.")
        self.next_turn()

    def shuffle_seats(self):
        """Rebuild the links in a random order (all nodes stay linked)."""
        players = list(self.traverse())
        random.shuffle(players)
        for index, player in enumerate(players):
            player.next = players[(index + 1) % len(players)]
            player.prev = players[index - 1]
        self.head = players[0]
        self._record("🔀 Se mezclaron los puestos de la mesa.")

    def reset(self):
        self.__init__()

    # ------------------------------------------------------------ serialization
    def to_dict(self):
        return {
            "players": [p.to_dict() for p in self.traverse()],
            "head": self.head.name if self.head else None,
            "tail": self.head.prev.name if self.head else None,
            "current": self.current.name if self.current else None,
            "clockwise": self.clockwise,
            "size": self.size,
            "winners": self.winners,
            "log": self.log,
        }
