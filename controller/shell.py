from code import InteractiveConsole
from datastructures.basic import InteractiveDataStructure
from threading import Thread
from contextlib import redirect_stdout, redirect_stderr
import sys
from importlib import import_module


class MyStdOut(object):
    def __init__(self, console):
        self.console = console

    def write(self, data):
        self.console.add_line(data, is_command=False)

    def flush(self):
        self.console.clear_input()


class VariableEnvironment(dict):
    def __init__(self):
        """
        Handles variables created by
        user in console.
        """
        super().__init__()
        self.variables = {}
        self.recently_touched = []

    def __getitem__(self, var_name):
        """
        Update a data structure's state
        any time it gets accessed.
        """
        # clone may not be implemented
        # try:
        #     reference = self.variables[var_name]
        #     if isinstance(reference, InteractiveDataStructure):
        #         reference.add_state_to_history()
        # except NotImplementedError:
        #     # clone not implemented,
        #     # cant update history
        #     pass
        # finally:
        #     # append to recents list for redrawing
        #     self.recently_touched.append(var_name)

        return self.variables[var_name]

    def __setitem__(self, var_name, value):
        self.variables[var_name] = value

    def __delitem__(self, var_name):
        del self.variables[var_name]


class EmbeddedShell(InteractiveConsole):

    def __init__(self, console, locals=None):
        """
        Embedded python console for easy creation of lists,
        handling of loops, and interacting with data structure objects.
        :param console: tkinter Console object from view module
        :param locals: dict of local variables
        """
        super().__init__(locals)
        self.locals = VariableEnvironment()
        self.console = console
        self.my_std_out = MyStdOut(self.console)

        self.runcode("from datastructures.arrays import *")
        self.runcode("from datastructures.tree import BST, BinaryHeap")
        self.runcode("from datastructures.graph import Graph")

    def runcode(self, code):
        # reset list of recently touched data structures
        self.locals.recently_touched = []
        with redirect_stdout(self.my_std_out):
            try:
                # use temp_var to get return value from exec
                self.locals["TEMP_VAR"] = None

                # try to assign return value to TEMP_VAR
                try:
                    exec("TEMP_VAR = " + code, self.locals)
                except SyntaxError:
                    exec(code, self.locals)

                # print return value if any
                if self.locals["TEMP_VAR"] and "print" not in code \
                        and "=" not in code:
                    print(self.locals["TEMP_VAR"])

                # clean up namespace
                del self.locals["TEMP_VAR"]

            except SystemExit:
                raise
            except Exception as e:
                self.showtraceback()
                print("[ERROR]: " + str(e))

        # return list of recently touched data structures for redrawing
        return self.locals.recently_touched

    def push(self, line):
        self.console.add_line(line, is_command=False)

    def write(self, data):
        self.console.add_line(data, is_command=False)


