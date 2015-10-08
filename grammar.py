#! /usr/bin/python
import sys
import cmd

# ----------------------------------------------------------------------------------------------------

class Option:

    def __init__(self, lsemantic = "", conjs = None):
        self.lsemantic = lsemantic
        if conjs:
            self.conjuncts = conjs
        else:
            self.conjuncts = []

    def __repr__(self):
        return "(\"%s\", %s)" % (self.lsemantic, self.conjuncts)

# ----------------------------------------------------------------------------------------------------

class Conjunct:

    def __init__(self, name, rsemantic = "", is_variable = False):
        self.name = name
        self.rsemantic = rsemantic
        self.is_variable = is_variable

    def __repr__(self):
        return self.name

# ----------------------------------------------------------------------------------------------------

class Rule:

    def __init__(self, lname):
        self.lname = lname
        self.options = []

# ----------------------------------------------------------------------------------------------------

class Tree:

    def __init__(self, option):
        self.option = option
        self.subtrees = [None for c in self.option.conjuncts]
        self.parent = None
        self.parent_idx = 0

    def next(self, idx):
        if idx + 1 < len(self.option.conjuncts):
            return (self, idx + 1)
        else:
            if self.parent:
                return self.parent.next(self.parent_idx)
            else:
                return (None, 0)

    def add_subtree(self, idx, tree):
        tree.parent = self
        tree.parent_idx = idx
        self.subtrees[idx] = tree
        return tree

    def __repr__(self):
        return str(zip(self.option.conjuncts, self.subtrees))

# ----------------------------------------------------------------------------------------------------

# Returns (name, semantics, remaining_str)
# For example for "VP[X, Y] foo bar" it returns:
#     ("VP", "X, Y", "foo bar")
#
def parse_next_atom(s):
    s = s.strip()

    for i in range(0, len(s)):
        c = s[i]
        if c == ' ':
            return (s[:i], "", s[i:].strip())
        elif c == '[':
            j = s.find("]", i)
            if j < 0:
                raise Exception
            return (s[:i], s[i+1:j], s[j+1:].strip())

    return (s, "", "")

# ----------------------------------------------------------------------------------------------------

class Grammar:

    def __init__(self):
        self.rules = {}

    def add_rule(self, s):
        tmp = s.split(" -> ")
        if len(tmp) != 2:
            raise Exception

        (lname, lsem, outstr) = parse_next_atom(tmp[0].strip())

        # See if a rule with this lname already exists. If not, add it
        if lname in self.rules:
            rule = self.rules[lname]
        else:
            rule = Rule(lname)
            self.rules[lname] = rule

        opt_strs = tmp[1].split("|")

        for opt_str in opt_strs:
            opt_str = opt_str.strip()

            opt = Option(lsem)

            while opt_str:
                (rname, rsem, opt_str) = parse_next_atom(opt_str)
                is_variable = rname[0].isupper()
                opt.conjuncts += [Conjunct(rname, rsem, is_variable)]

            rule.options += [opt]

    def enum_id(self, L):
        return [ Option("cabinet-12", [Conjunct("cabinet-12")]),
                 Option("chair-3",    [Conjunct("chair-3")]) ]

    def enum_type(self, L):
        return [ Option("table", [Conjunct("table")]),
                 Option("drink", [Conjunct("drink")]) ]

    def get_semantics(self, tree):

        sem = tree.option.lsemantic
        for i in range(0, len(tree.subtrees)):
            conj = tree.option.conjuncts[i]
            subtree = tree.subtrees[i]

            if subtree:
                child_sem = self.get_semantics(subtree)
                sem = sem.replace(conj.rsemantic, child_sem)

        return sem

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def parse(self, target, words):
        if not target in self.rules:
            return False

        rule = self.rules[target]

        for opt in rule.options:
            T = Tree(opt)
            if self._parse((T, 0), words) != False:
                return self.get_semantics(T)

        return False

    def _parse(self, TIdx, words):
        (T, idx) = TIdx

        if not T:
            return words == []

        if not words:
            return False

        conj = T.option.conjuncts[idx]

        if conj.is_variable:
            if not conj.name in self.rules:
                return False
            options = self.rules[conj.name].options

        elif conj.name[0] == "$":
            options = getattr(self, "enum_" + conj.name[1:])(words)

        else:
            if conj.name == words[0]:
                return self._parse(T.next(idx), words[1:])
            else:
                return False

        for opt in options:
            subtree = T.add_subtree(idx, Tree(opt))
            ret = self._parse((subtree, 0), words)
            if ret:
                return ret

        return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def next_word(self, target, words):
        if not target in self.rules:
            return False

        rule = self.rules[target]

        next_words = []
        for opt in rule.options:
            next_words += self._next_word((Tree(opt), 0), words)

        return next_words

    def _next_word(self, TIdx, words):
        (T, idx) = TIdx

        if not T:
            return []

        conj = T.option.conjuncts[idx]

        if conj.is_variable:
            if not conj.name in self.rules:
                return []
            options = self.rules[conj.name].options

        elif conj.name[0] == "$":
            options = getattr(self, "enum_" + conj.name[1:])(words)

        else:
            if words == []:
                return [conj.name]
            elif conj.name == words[0]:
                return self._next_word(T.next(idx), words[1:])
            else:
                return []

        next_words = []
        for opt in options:
            subtree = T.add_subtree(idx, Tree(opt))
            next_words += self._next_word((subtree, 0), words)

        return next_words

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
            #print self.parser.check(["C"], command.strip().split(" "))
            print self.parser.parse("C", command.strip().split(" "))

        return False

    def completedefault(self, text, line, begidx, endidx):
        try:
            partial_command = line.split(" ")[:-1]
            words = self.parser.next_word("C", partial_command)
        except Exception as e:
            print e

        return [w + " " for w in words if w.startswith(text)]

# ----------------------------------------------------------------------------------------------------

def main():
    g = Grammar()

    g.add_rule("C[{\"robot\": R, A}] -> Robot[R] VP[A]")
    g.add_rule("C[{A}] -> VP[A]")

    g.add_rule("Robot[\"amigo\"] -> amigo")
    g.add_rule("Robot[\"sergio\"] -> sergio")

    g.add_rule("VP[\"action\": A] -> V[A]")
    g.add_rule("VP[\"action\": A, \"entity\": {E}] -> V[A] NP[E]")

    g.add_rule("NP[\"id\": I] -> ID[I]")
    g.add_rule("NP[\"type\": T] -> DET TYPE[T]")
    g.add_rule("NP[\"type\": T, \"color\": C] -> DET COLOR[C] TYPE[T]")

    g.add_rule("COLOR[\"green\"] -> green")
    g.add_rule("COLOR[\"blue\"] -> blue")

    g.add_rule("V[\"grasp\"] -> grab | grasp | pick up")
    g.add_rule("V[\"move\"] -> move to | goto | go to")

    g.add_rule("DET -> the")
    g.add_rule("ID[\"X\"] -> $id[X]")
    g.add_rule("TYPE[\"X\"] -> object[X] | $type[X]")

    try:
        repl = REPL(g)
        repl.cmdloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    sys.exit(main())
