#! /usr/bin/python
import sys

# ----------------------------------------------------------------------------------------------------

class Grammar:

    def __init__(self):
        self.rules = {}

    def add_rule(self, s):
        r = s.split(" -> ")
        if len(r) != 2:
            raise Exception

        t = r[0].strip()
        opts = r[1].split("|")

        for opt in opts:
            opt = opt.strip()
            cs = opt.split(" ")

            if not t in self.rules:
                self.rules[t] = [cs]
            else:
                self.rules[t] += [cs]

    def check_id(self, L):
        print "ID: %s" % L

        if not L:
            return False

        if L[0] in ["cabinet"]:
            return L[1:]

        return False

    def check(self, T, L):       
        print "check(%s, %s)" % (T, L)

        if not T:
            return L == []

        if not L:
            return False

        t = T[0]
        if t[0] == "$":
            ret = getattr(self, "check_" + t[1:])(L)
            if ret == False:
                return False
            else:
                return self.check(T[1:], ret)

        if not t[0].isupper():
            if L[0] == t:
                return self.check(T[1:], L[1:])
            else:
                return False

        if not t in self.rules:
            return False

        opts = self.rules[t]
        for opt in opts:
            if self.check(opt + T[1:], L):
                return True

        return False

# ----------------------------------------------------------------------------------------------------

def main():
    g = Grammar()

    g.add_rule("VP -> V")
    g.add_rule("VP -> V NP")
    g.add_rule("NP -> Id")
    g.add_rule("NP -> Det Id")
    g.add_rule("NP -> Det Type")

    g.add_rule("V -> grab | grasp | move to")
    g.add_rule("Det -> the")
    g.add_rule("Id -> $id")

    print g.check(["VP"], ["grasp"])
    print g.check(["VP"], ["move", "to", "the", "cabinet"])

if __name__ == "__main__":
    sys.exit(main())
