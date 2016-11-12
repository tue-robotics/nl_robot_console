import unittest
from ..cfgparser import CFGParser
from ..cfgparser import parse_next_atom


class TestCfgParser(unittest.TestCase):
    def test_add_rule_1(self):
        parser = CFGParser()

        self.assertEqual(len(parser.rules), 0)

        parser.add_rule("""SIDE["left"] -> left""")

        self.assertEqual(len(parser.rules), 1)

        rule = parser.rules["SIDE"]
        self.assertEqual(rule.lname, "SIDE")
        self.assertEqual(len(rule.options), 1)

    def test_add_rule_2(self):
        parser = CFGParser()

        self.assertEqual(len(parser.rules), 0)

        parser.add_rule("""SIDE["left"] -> left""")

        self.assertEqual(len(parser.rules), 1)

        rule = parser.rules["SIDE"]
        self.assertEqual(rule.lname, "SIDE")

class TestParseNextAtom(unittest.TestCase):
    def test_parse_next_atom_1(self):
        (name, semantics, remaining) = parse_next_atom("""SIDE["left"]""")

        self.assertEqual(name, "SIDE")
        self.assertEqual(semantics, '"left"')
        self.assertEqual(remaining, '')

    def test_parse_next_atom_2(self):
        (name, semantics, remaining) = parse_next_atom("""VP["action": A]""")

        self.assertEqual(name, "VP")
        self.assertEqual(semantics, '"action": A')
        self.assertEqual(remaining, '')

    def test_parse_next_atom_3(self):
        (name, semantics, remaining) = parse_next_atom("""VP["action": "arm-goal", "symbolic": "reset", "side": S]""")

        self.assertEqual(name, "VP")
        self.assertEqual(semantics, '"action": "arm-goal", "symbolic": "reset", "side": S')
        self.assertEqual(remaining, '')


