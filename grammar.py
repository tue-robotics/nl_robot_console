#! /usr/bin/python
import sys
import cmd

# ----------------------------------------------------------------------------------------------------

def parse_next_conj(instr):
    instr = instr.strip()

    if not instr:
        return None

    i = instr.find("[")
    i_space = instr.find(" ")

    if i >= 0:
        if i_space >= 0 and i_space < i:
            return (instr[:i_space], "", instr[i_space:])
        j = instr.find("]", i)
        if j < 0:
            raise Exception
        return (instr[:i], instr[i:j+1], instr[j+1:])
    else:
        i = instr.find(" ")
        if i < 0:
            return (instr, "", "")
        else:
            return (instr[:i], "", instr[i:])

# ----------------------------------------------------------------------------------------------------

class Tree:

    def __init__(self, types = []):
        self.types = types
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

    def add_subtree(self, idx, types):
        subtree = Tree(types)
        subtree.parent = self
        subtree.parent_idx = idx
        self.subtrees[idx] = subtree
        return subtree

# ----------------------------------------------------------------------------------------------------

class Grammar:

    def __init__(self):
        self.rules = {}

    def add_rule(self, s):
        r = s.split(" -> ")
        if len(r) != 2:
            raise Exception

        (t, t_sem, outstr) = parse_next_conj(r[0].strip())

        opts = r[1].split("|")

        for opt in opts:
            opt = opt.strip()

            cs = []
            while True:
                ret = parse_next_conj(opt)
                if not ret:
                    break

                print ret

                (c, sem, opt) = ret
                cs += [c]

            if not t in self.rules:
                self.rules[t] = [cs]
            else:
                self.rules[t] += [cs]

    def enum_id(self, L):
        return [["cabinet-12"], ["chair-3"]]

    def enum_type(self, L):
        return [["drink"], ["table"]]

    def parse(self, types, words):
        T = Tree(types);
        if self._parse((T, 0), words):
            return T
        else:
            return False

    def _parse(self, TIdx, words):
        (T, idx) = TIdx

        if not T:
            return words == []

        if not words:
            return False

        t = T.types[idx]

        if t[0] == "$":
            opts = getattr(self, "enum_" + t[1:])(words)

        elif t[0].isupper():
            if not t in self.rules:
                return False
            opts = self.rules[t]
        else:
            if t == words[0]:
                return self._parse(T.next(idx), words[1:])
            else:
                return False

        for opt in opts:
            subtree = T.add_subtree(idx, opt)
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
            print self.parser.parse(["C"], command.strip().split(" "))

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
    
    g.add_rule("Robot[robot=amigo] -> amigo")
    g.add_rule("Robot[robot=sergio] -> sergio")
    
    g.add_rule("VP[action=A] -> V[A]")
    g.add_rule("VP[action=A, entity=E] -> V[A] NP[E]")
    #g.add_rule("VP[action=A, entity=E, loc=E2] -> V[A] NP[E] from NP[E2]")
    
    g.add_rule("NP[unknown] -> Id")
    g.add_rule("NP[unknown] -> Det Type")
    g.add_rule("NP[unknown] -> Det Adj Type")
    
    g.add_rule("Adj -> green | blue | red | small | big | large")
    
    g.add_rule("V[action=grasp] -> grab | grasp | pick up")
    g.add_rule("V[action=move] -> move to | goto")
    
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
