import unittest
from ..cfgparser import CFGParser
from ..cfgparser import parse_next_atom


class TestCfgParser(unittest.TestCase):
    def test_add_rule_1(self):
        parser = CFGParser()

        self.assertEqual(len(parser.rules), 0)

        parser.add_rule("""SIDE["left"] -> left""")

        self.assertEqual(len(parser.rules), 1)

    def test_parse_next_atom_1(self):
        (name, semantics, remaining) = parse_next_atom("""SIDE["left"]""")

        self.assertEqual(name, "SIDE")
        self.assertEqual(semantics, '"left"')
        self.assertEqual(remaining, '')