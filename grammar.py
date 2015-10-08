#! /usr/bin/python
import sys
import cmd

# ----------------------------------------------------------------------------------------------------

# Returns (atom, remaining_str)
#    atom:          of type Atom
#    remaining_str: string with remaining atoms
def parse_next_atom(instr):
    instr = instr.strip()

    if not instr:
        return (None, "")

    i = instr.find("[")
    i_space = instr.find(" ")

    name = ""
    semantics = ""
    remaining_str = ""

    if i >= 0:
        if i_space >= 0 and i_space < i:
            name = instr[:i_space]
            remaining_str = instr[i_space:]
        else:
            j = instr.find("]", i)
            if j < 0:
                raise Exception
            else:
                name = instr[:i]
                semantics = instr[i+1:j]
                remaining_str = instr[j+1:]
    else:
        i = instr.find(" ")
        if i < 0:
            name = instr
        else:
            name = instr[:i]
            remaining_str = instr[i:]

    is_variable = name[0].isupper()
    a = Atom(name, semantics, is_variable)

    return (a, remaining_str)

# ----------------------------------------------------------------------------------------------------

class Tree:

    def __init__(self, types = [], parent_semantics = None):
        self.types = types
        self.parent_semantics = parent_semantics
        self.parent = None
        self.parent_idx = 0
        self.subtrees = [None for t in types]

    def next(self, idx):
        if idx + 1 < len(self.types):
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
        return str((self.parent_semantics, zip(self.types, self.subtrees)))

# ----------------------------------------------------------------------------------------------------

class Rule:

    def __init__(self, a, options):
        self.antecedent = a
        self.options = options

# ----------------------------------------------------------------------------------------------------

class Atom:

    def __init__(self, name, semantics, is_variable = False):
        self.name = name
        self.semantics = semantics
        self.is_variable = is_variable

    def __repr__(self):
        return str((self.name, self.semantics))

# ----------------------------------------------------------------------------------------------------

class Grammar:

    def __init__(self):
        self.rules = {}

    def add_rule(self, s):
        r = s.split(" -> ")
        if len(r) != 2:
            raise Exception

        (antc, outstr) = parse_next_atom(r[0].strip())

        opts = r[1].split("|")

        for opt_str in opts:
            opt_str = opt_str.strip()

            cs = []
            while True:
                (consq, opt_str) = parse_next_atom(opt_str)
                if not consq:
                    break
                cs += [consq]

            if not antc.name in self.rules:
                self.rules[antc.name] = Rule(antc, [cs])
            else:
                self.rules[antc.name].options += [cs]

    def enum_id(self, L):
        return [ [Atom("cabinet-12", "cabinet-12")],
                 [Atom("chair-3",    "chair-3")] ]

    def enum_type(self, L):
        return [ [Atom("table", "table")],
                 [Atom("drink", "drink")] ]

    def get_semantics(self, tree):
        sem = tree.parent_semantics
        if not sem:
            return ""

        #print tree

        for i in range(0, len(tree.types)):
            t = tree.types[i]
            subtree = tree.subtrees[i]

            if subtree:
                child_sem = self.get_semantics(subtree)
                if child_sem:
                    sem = sem.replace(t.semantics, child_sem)

        print sem
        return sem


    def parse(self, target, words):
        if not target in self.rules:
            return False

        rule = self.rules[target]
        parent_semantics = rule.antecedent.semantics
        opts = rule.options

        T = None
        for opt in opts:
            T_test = Tree(opt, parent_semantics)
            if self._parse((T_test, 0), words) != False:
                T = T_test
                break

        if not T:
            return False

        self._parse((T, 0), words)
        self.get_semantics(T)
        return T

    def _parse(self, TIdx, words):

        (T, idx) = TIdx

        if not T:
            return words == []

        if not words:
            return False

        t = T.types[idx]
        parent_semantics = None

        if t.name[0] == "$":
            opts = getattr(self, "enum_" + t.name[1:])(words)

        elif t.is_variable:
            if not t.name in self.rules:
                return False
            rule = self.rules[t.name]
            parent_semantics = rule.antecedent.semantics
            opts = rule.options
        else:
            if t.name == words[0]:
                return self._parse(T.next(idx), words[1:])
            else:
                return False

        for opt in opts:
            subtree = T.add_subtree(idx, Tree(opt, parent_semantics))
            ret = self._parse((subtree, 0), words)
            if ret:
                return ret

        return False

    def check(self, T, L):
        #print "check(%s, %s)" % (T, L)

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
            (opts, t_sem) = self.rules[t]

            print (opts, t_sem)

        for opt in opts:
            print opt
            ret = self.check([o[0] for o in opt] + T[1:], L)    # <-- this is where the magic should happen
            if ret != False:
                print "check(%s, %s)" % (T, L)
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
            #print self.parser.check(["C"], command.strip().split(" "))
            print self.parser.parse("C", command.strip().split(" "))

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

    g.add_rule("C[robot=R, command=A] -> Robot[R] VP[A]")
    g.add_rule("C[command=A] -> VP[A]")

    g.add_rule("Robot[amigo] -> amigo")
    g.add_rule("Robot[sergio] -> sergio")

    #g.add_rule("VP[A] -> V[A]")
    g.add_rule("VP[A(E)] -> V[A] NP[E]")
    #g.add_rule("VP[action=A, entity=E, loc=E2] -> V[A] NP[E] from NP[E2]")

    g.add_rule("NP[X] -> Id[X]")
    g.add_rule("NP[X] -> Det Type[X]")
    g.add_rule("NP[X] -> Det Adj Type[X]")

    g.add_rule("Adj -> green | blue | red | small | big | large")

    g.add_rule("V[grasp] -> grab | grasp | pick up")
    g.add_rule("V[move] -> move to | goto")

    g.add_rule("Det -> the")
    g.add_rule("Id[X] -> $id[X]")
    g.add_rule("Type[X] -> object[X] | $type[X]")

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
