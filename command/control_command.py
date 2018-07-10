
class ClearConsoleCommand(object):
    def __init__(self, receiver, should_redraw=False):
        """
        Clears the console history visually and clears deque.
        Created by a ControlCommandFactory and passed to
        DrawControl for execution.
        """
        self.receiver = receiver
        self.should_redraw = should_redraw

    def execute(self):
        self.receiver.view.console.clear_console()

    def undo(self):
        """Currently not implemented"""
        pass

    def __repr__(self):
        return "Clearing canvas."


class CreateVariableCommand(object):
    def __init__(self, receiver, var_name, *other_args, should_redraw=True):
        """
        Creates a binding from a variable name to a
        reference returned by bst.find() or similar contained
        in *other_args. Get the value returned by this nested command
        and assign it in the my_variables dictionary.

        Binding is contained in control class inside
        my_variables
        """
        self.receiver = receiver
        self.should_redraw = should_redraw
        self.var_name = var_name
        self.nested_command = "".join([str(arg) + " " for arg in other_args])

    def execute(self):
        """
        Executes nested_command to get value that
        is being assigned to var_name.
        """
        # don't call process_command so nested command
        # doesn't get printed on an extra line
        command_obj = self.receiver.parse_command(self.nested_command)
        reference = self.receiver.perform_command(command_obj)

        self.receiver.my_variables[self.var_name] = reference

    def undo(self):
        self.receiver.my_variables[self.var_name] = None

    def __repr__(self):
        return "ASSIGN '%s' to reference returned by '%s'" % (self.var_name, self.nested_command)


class PrintVariableCommand(object):
    def __init__(self, receiver, var_name, should_redraw=False):
        """
        Print a value stored by variable name in control.my_variables

        :param receiver: control object receiving action
        :param var_name: name used as index in my_variables
        :param should_redraw: used for all commands
        """

        self.receiver = receiver
        self.var_name = var_name
        self.should_redraw = should_redraw

    def execute(self):
        """
        Gets value/reference from dictionary stored in
        control object (possible key error)
        and print it to console.
        """
        try:
            value = self.receiver.my_variables[self.var_name]
        except KeyError:
            raise KeyError("Variable name '%s' is not defined" % self.var_name)

        self.receiver.view.console.add_line(value, is_command=False)

    def undo(self):
        pass



