from code import InteractiveConsole
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


class EmbeddedShell(InteractiveConsole):

    def __init__(self, console, locals=None, filename=None):
        super().__init__(locals, filename)
        self.console = console
        self.my_std_out = MyStdOut(self.console)

        self.datastructures = import_module("datastructures.tree")

    def runcode(self, code):
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
                if self.locals["TEMP_VAR"] and "print" not in code:
                    print(self.locals["TEMP_VAR"])

                # clean up namespace
                del self.locals["TEMP_VAR"]

            except SystemExit:
                raise
            except Exception as e:
                self.showtraceback()
                print("[ERROR]: " + str(e))

    def push(self, line):
        self.console.add_line(line, is_command=False)

    def write(self, data):
        self.console.add_line(data, is_command=False)


