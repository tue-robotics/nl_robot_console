#! /usr/bin/python
import sys
import cmd

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

    def enum_id(self, L):
        return [["cabinet-12"], ["chair-3"]]

    def enum_type(self, L):
        return [["drink"], ["table"]]

    def check(self, T, L):       
        # print "check(%s, %s)" % (T, L)

        if not T:
            return L == []

        if not L:
            return False

        t = T[0]

        if t[0] == "$":
            opts = getattr(self, "enum_" + t[1:])(L)

        elif not t[0].isupper():
            if L[0] == t:
                return self.check(T[1:], L[1:])
            else:
                return False
        else:
            if not t in self.rules:
                return False
            opts = self.rules[t]

        for opt in opts:
            if self.check(opt + T[1:], L):
                return True

        return False

    def next_word(self, T, L):
        if not T:
            return []

        t = T[0]

        if t[0] == "$":
            opts = getattr(self, "enum_" + t[1:])(L)

        elif not t[0].isupper():
            if L == []:
                return [t]
            elif L[0] == t:
                return self.next_word(T[1:], L[1:])
            else:
                return []
        else:
            if not t in self.rules:
                return []
            opts = self.rules[t]

        words = []
        for opt in opts:
            words += self.next_word(opt + T[1:], L)

        return words

# ----------------------------------------------------------------------------------------------------

class REPL(cmd.Cmd):

    def __init__(self, parser):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.use_rawinput = True
        self.parser = parser

    def emptyline(self):
        pass

    def do_help(self, str):
        print "help"

    def default(self, command):
        if not command:
            return False
        elif command in ["quit", "exit"]:
            return True  # True means interpreter has to stop
        else:
            print self.parser.check(["C"], command.strip().split(" "))

        return False

    def completedefault(self, text, line, begidx, endidx):
        try:
            partial_command = line.split(" ")[:-1]
            words = self.parser.next_word(["C"], partial_command)
        except Exception as e:
            print e

        return [w + " " for w in words if w.startswith(text)]

# ----------------------------------------------------------------------------------------------------

def main():
    g = Grammar()

    g.add_rule("C -> Robot VP")
    g.add_rule("C -> VP")
    g.add_rule("Robot -> amigo | sergio")
    g.add_rule("VP -> V")
    g.add_rule("VP -> V NP")
    g.add_rule("NP -> Id")
    g.add_rule("NP -> Det Type")
    g.add_rule("NP -> Det Adj Type")
    g.add_rule("Adj -> green | blue | red | small | big | large")
    g.add_rule("V -> grab | grasp | move to | goto")
    g.add_rule("Det -> the")
    g.add_rule("Id -> $id")
    g.add_rule("Type -> object | $type")

    #print g.check(["C"], "grasp".split(" "))
    #print g.check(["C"], "move to the cabinet".split(" "))

    #print g.next_word(["C"], "amigo move to".split(" "))

    try:
        repl = REPL(g)
        repl.cmdloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    sys.exit(main())
