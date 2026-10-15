"""Run:  python -m unittest -v"""

import unittest

from turn_table import TurnTable


def names(table, clockwise=True):
    return [p.name for p in table.traverse(clockwise=clockwise)]


class TurnTableTest(unittest.TestCase):
    def setUp(self):
        self.table = TurnTable()
        for name in ("Ana", "Beto", "Caro", "Dani"):
            self.table.join_player(name)

    def assert_fully_linked(self):
        """Every node must be linked both ways and the circle must close."""
        for player in self.table.traverse():
            self.assertIs(player.next.prev, player)
            self.assertIs(player.prev.next, player)

    def test_join_links_last_with_first(self):
        self.assertEqual(names(self.table), ["Ana", "Beto", "Caro", "Dani"])
        self.assertEqual(self.table.head.prev.name, "Dani")
        self.assertEqual(self.table.head.prev.next.name, "Ana")
        self.assert_fully_linked()

    def test_single_player_points_to_itself(self):
        table = TurnTable()
        solo = table.join_player("Solo")
        self.assertIs(solo.next, solo)
        self.assertIs(solo.prev, solo)

    def test_join_after(self):
        self.table.join_player_after("Eva", "Beto")
        self.assertEqual(names(self.table), ["Ana", "Beto", "Eva", "Caro", "Dani"])
        self.assert_fully_linked()

    def test_backwards_traversal(self):
        self.assertEqual(names(self.table, clockwise=False), ["Ana", "Dani", "Caro", "Beto"])

    def test_eliminate_head_and_current(self):
        self.table.eliminate_player("Ana")
        self.assertEqual(self.table.head.name, "Beto")
        self.assertEqual(self.table.current.name, "Beto")
        self.assertEqual(names(self.table), ["Beto", "Caro", "Dani"])
        self.assert_fully_linked()

    def test_eliminate_last_remaining(self):
        table = TurnTable()
        table.join_player("Solo")
        table.eliminate_player("Solo")
        self.assertTrue(table.is_empty())
        self.assertEqual(table.size, 0)

    def test_turns_never_end(self):
        for _ in range(4):
            self.table.next_turn()
        self.assertEqual(self.table.current.name, "Ana")

    def test_reverse_card(self):
        self.table.play_reverse()
        self.assertFalse(self.table.clockwise)
        self.assertEqual(self.table.current.name, "Dani")

    def test_skip_and_draw_two(self):
        self.table.play_skip()
        self.assertEqual(self.table.current.name, "Caro")
        self.table.play_draw_two()
        self.assertEqual(self.table.find_player("Dani").cards, 9)
        self.assertEqual(self.table.current.name, "Ana")

    def test_winner_leaves_the_table(self):
        self.table.find_player("Ana").cards = 1
        self.table.play_number()
        self.assertEqual(self.table.winners, ["Ana"])
        self.assertIsNone(self.table.find_player("Ana"))
        self.assertEqual(self.table.current.name, "Beto")
        self.assert_fully_linked()

    def test_shuffle_keeps_everyone_linked(self):
        self.table.shuffle_seats()
        self.assertEqual(sorted(names(self.table)), ["Ana", "Beto", "Caro", "Dani"])
        self.assert_fully_linked()

    def test_duplicate_name_rejected(self):
        with self.assertRaises(ValueError):
            self.table.join_player("ana")


if __name__ == "__main__":
    unittest.main()
