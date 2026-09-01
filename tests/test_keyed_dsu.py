import unittest

from utils import KeyedDSU


class KeyedDSUTests(unittest.TestCase):
    def test_accepts_hashable_non_integer_keys(self):
        dsu = KeyedDSU(["alice", "bob", "carol", (1, 2)])

        self.assertTrue(dsu.union("alice", "bob"))
        self.assertFalse(dsu.union("bob", "alice"))
        self.assertTrue(dsu.same("alice", "bob"))
        self.assertFalse(dsu.same("alice", "carol"))
        self.assertEqual(dsu.size("bob"), 2)
        self.assertEqual(dsu.components, 3)
        self.assertEqual(dsu.component_count, 3)
        self.assertEqual(len(dsu), 4)

    def test_roots_members_and_groups(self):
        dsu = KeyedDSU(["alice", "bob", "carol", (1, 2)])
        dsu.union("alice", "bob")

        self.assertEqual(dsu.roots(), {"alice", "carol", (1, 2)})
        self.assertEqual(dsu.members("bob"), ["alice", "bob"])
        self.assertEqual(
            dsu.groups(),
            {
                "alice": ["alice", "bob"],
                "carol": ["carol"],
                (1, 2): [(1, 2)],
            },
        )

        groups = dsu.groups()
        groups["alice"].clear()
        self.assertEqual(dsu.members("alice"), ["alice", "bob"])

    def test_adds_keys_dynamically_without_duplicating_them(self):
        dsu = KeyedDSU[str]()

        self.assertTrue(dsu.add("new"))
        self.assertFalse(dsu.add("new"))
        self.assertIn("new", dsu)
        self.assertEqual(len(dsu), 1)
        self.assertEqual(dsu.components, 1)

    def test_find_fully_compresses_path(self):
        dsu = KeyedDSU("abcdef")
        dsu.parent.update(
            {
                "a": "a",
                "b": "a",
                "c": "b",
                "d": "c",
                "e": "d",
                "f": "e",
            }
        )

        self.assertEqual(dsu.find("f"), "a")
        self.assertTrue(all(dsu.parent[key] == "a" for key in "abcdef"))

    def test_unknown_keys_fail_visibly(self):
        dsu = KeyedDSU(["known"])

        with self.assertRaisesRegex(KeyError, "unknown key"):
            dsu.find("missing")
        with self.assertRaises(KeyError):
            dsu.union("known", "missing")
        with self.assertRaises(KeyError):
            dsu.members("missing")

    def test_rejects_unhashable_keys(self):
        dsu = KeyedDSU()

        with self.assertRaises(TypeError):
            dsu.add([])
