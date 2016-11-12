import unittest
from ..cfgparser import CFGParser


class TesCfgParser(unittest.TestCase):
    def testAddRule(self):
        parser = CFGParser()