#! /usr/bin/python
import sys
import cmd
import cfgparser

# ----------------------------------------------------------------------------------------------------

class REPL(cmd.Cmd):

    def __init__(self, grammar_filename):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.use_rawinput = True
        self.grammar_filename = grammar_filename
        self._load_grammar()

    def _load_grammar(self):
        self.parser = cfgparser.CFGParser.fromfile(self.grammar_filename)
        self.parser.set_function("id", self.enum_id)
        self.parser.set_function("type", self.enum_type)
        self.parser.set_function("number", self.enum_number)

    def emptyline(self):
        pass

    def do_help(self, str):
        print """
        Write a command in natural language. You can either prefix the
        command with a robot name, or leave it out and the command will
        be sent to the last robot specified.

        Examples:

            amigo go to the kitchen
            amigo grab the green drink from the table
            go to 2.45 -0.67
            grab the drink with left
            turn right
            turn 45 degrees left

        *Note that tab-completion is available!*

        Some special commands:

            reload - reloads the grammar
            help   - shows this
            exit   - quits
        """

    def default(self, command):
        if not command:
            return False
        elif command in ["quit", "exit"]:
            return True  # True means interpreter has to stop
        elif command in ["reload"]:
            self._load_grammar()
        else:
            print ""
            print "    Meaning: %s" % self.parser.parse("C", command.strip().split(" "))
            print ""

        return False

    def completedefault(self, text, line, begidx, endidx):
        try:
            partial_command = line.split(" ")[:-1]
            words = self.parser.next_word("C", partial_command)
        except Exception as e:
            print e

        return [w + " " for w in words if w.startswith(text)]

    # ---------------------------------------

    def enum_id(self, L):
        return [ cfgparser.Option("cabinet-12", [cfgparser.Conjunct("cabinet-12")]),
                 cfgparser.Option("chair-3",    [cfgparser.Conjunct("chair-3")]) ]

    def enum_type(self, L):
        return [ cfgparser.Option("living_room", [cfgparser.Conjunct("living"), cfgparser.Conjunct("room")]),
                 cfgparser.Option("kitchen", [cfgparser.Conjunct("kitchen")]),
                 cfgparser.Option("table", [cfgparser.Conjunct("table")]),
                 cfgparser.Option("drink", [cfgparser.Conjunct("drink")]),
                 cfgparser.Option("bar", [cfgparser.Conjunct("bar")]),
                 cfgparser.Option("exit", [cfgparser.Conjunct("exit")]),
                 cfgparser.Option("cabinet", [cfgparser.Conjunct("cabinet")]) ]

    def enum_number(self, L):
        if not L:
            return [cfgparser.Option("", [cfgparser.Conjunct("<NUMBER>")])]
        try:
            f = float(L[0])
            return [cfgparser.Option(L[0], [cfgparser.Conjunct(L[0])])]
        except ValueError:
            return []

# ----------------------------------------------------------------------------------------------------

def main():

    import sys, os
    pkgdir = os.path.dirname(sys.argv[0])

    try:
        repl = REPL(os.path.join(pkgdir, "grammar.fcfg"))
        repl.cmdloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    sys.exit(main())
