#! /usr/bin/python
import sys
import cmd
import cfgparser

# Connection to robot
import rospy
import action_server
from action_server import srv

# Connection to world model
import ed
from ed import srv

# ----------------------------------------------------------------------------------------------------

class RobotConnection:

    def __init__(self, robot_name):
        self.robot_name = robot_name
        self.cl_robot = rospy.ServiceProxy(self.robot_name + "/action_server/add_action", action_server.srv.AddAction)
        self.cl_wm = rospy.ServiceProxy(self.robot_name + "/ed/simple_query", ed.srv.SimpleQuery)

# ----------------------------------------------------------------------------------------------------

class REPL(cmd.Cmd):

    def __init__(self, grammar_filename):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.use_rawinput = True
        self.grammar_filename = grammar_filename
        self._load_grammar()

        # Default robot connection
        self.robot_connection = None
        self.robot_to_connection = {}
        self._get_or_create_robot_connection("amigo")

        self._clear_caches()

    def _load_grammar(self):
        self.parser = cfgparser.CFGParser.fromfile(self.grammar_filename)
        self.parser.set_function("id", self.enum_id)
        self.parser.set_function("type", self.enum_type)
        self.parser.set_function("number", self.enum_number)
        self.parser.set_function("property", self.enum_property)

    def _clear_caches(self):
        self._entities = []
        self._updated_wm = False

    def _get_or_create_robot_connection(self, robot_name):
        self.prompt = "[%s] > " % robot_name

        if not robot_name in self.robot_to_connection:
            self.robot_connection = RobotConnection(robot_name)
            self.robot_to_connection[robot_name] = self.robot_connection
        else:
            self.robot_connection = self.robot_to_connection[robot_name]

        return self.robot_connection

    def _update_wm(self):
        if self._updated_wm:
            return

        try:
            self._entities = self.robot_connection.cl_wm().entities
        except rospy.service.ServiceException, e:
            print("\n\n    %s\n" % e)

        self._updated_wm = True

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
            sem = self.parser.parse("C", command.strip().split(" "))
            if sem == False:
                print("\n    I do not understand.\n")
                return False

            import yaml
            params = yaml.load(sem)

            if "robot" in params:
                robot_name = params["robot"]
                self._get_or_create_robot_connection(robot_name)

            if not self.robot_connection:
                print("\n    Please specify which robot to use.\n")
                return False

            if "action" in params:
                action = params["action"]
            else:
                print("\n    No action specified in semantics:\n        %s\n" % sem)
                return False

            try:
                resp = self.robot_connection.cl_robot(action=action, parameters=sem)
                if (resp.error_msg):
                    print "\n    Error message from action server:\n\n        %s\n" % resp.error_msg
            except rospy.ServiceException, e:
                print("\n    Service call failed: %s\n" % e)

            # print "\n    Meaning: %s\n" % sem

        return False

    def postcmd(self, stop, line):
        # After a command is processed, clear the caches (e.g. world model entities)
        self._clear_caches()
        return stop

    def completedefault(self, text, line, begidx, endidx):
        try:
            partial_command = line.split(" ")[:-1]
            words = self.parser.next_word("C", partial_command)
        except Exception as e:
            print e

        return [w + " " for w in words if w.startswith(text)]

    # ---------------------------------------

    def enum_id(self, L):
        self._update_wm()

        ids = [e.id for e in self._entities]

        opts = []
        for id in ids:
            if id != "":
                opts += [cfgparser.Option(id, [cfgparser.Conjunct(id)])]

        return opts

    def enum_type(self, L):
        self._update_wm()

        types = set([i for sublist in [e.types for e in self._entities] for i in sublist])

        opts = []
        for t in types:
            if t != "":
                opts += [cfgparser.Option(t, [cfgparser.Conjunct(t)])]

        return opts

    def enum_property(self, L):
        options = []

        colors = ["red", "green", "blue", "yellow", "brown", "orange", "black", "white", "pink", "purple", "gray"]
        options += [cfgparser.Option("\"color\": \"%s\"" % c, [cfgparser.Conjunct(c)]) for c in colors ]

        sizes = ["large", "medium", "small"]
        options += [cfgparser.Option("\"size\": \"%s\"" % s, [cfgparser.Conjunct(s)]) for s in sizes ]

        return options

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