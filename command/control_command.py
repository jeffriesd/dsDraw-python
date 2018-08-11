from tkinter import Canvas
import datastructures


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
    def __init__(self, receiver, var_name, *other_args, should_redraw=False):
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
        self.nested_command = "".join([str(arg) + " " for arg in other_args]).strip()

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
        del self.receiver.my_variables[self.var_name]

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


class CreateDataStructureCommand(object):
    def __init__(self, receiver, model_type_name, *other_args, should_redraw=False):
        """
        Returns a new empty model created by ModelFactory.
        e.g. 'create bst'
        """
        self.receiver = receiver
        self.should_redraw = should_redraw
        self.model_name = model_type_name
        self.other_args = other_args
        self.factory = datastructures.ModelFactory()

    def execute(self):
        return self.factory.create_model(self.model_name, *self.other_args)

    def undo(self):
        del self.receiver.my_models[self.model_name]

    def __repr__(self):
        return "CREATED NEW %s" % self.model_name


class ShowRenderCommand(object):
    def __init__(self, receiver, model_name, should_redraw=True):
        self.receiver = receiver
        self.model_name = model_name
        self.should_redraw = should_redraw

    def execute(self):
        self.receiver.add_model_to_view(self.model_name)

    def undo(self):
        close_cmd = CloseRenderCommand(self.receiver, self.model_name, self.should_redraw)
        close_cmd.execute()

    def __repr__(self):
        return "ADDED %s TO VIEW" % self.model_name


class CloseRenderCommand(object):
    def __init__(self, receiver, model_name, should_redraw=True):
        """
        Removes key from control.my_renders dict and destroys
        canvas object from view.canvas.children
        """
        self.receiver = receiver
        self.model_name = model_name
        self.should_redraw = should_redraw

    def execute(self):
        self.receiver.my_renders.pop(self.model_name)
        self.receiver.view.canvas.get_child(self.model_name).destroy()

        renders = list(self.receiver.my_renders.keys())

        # close and reopen the rest
        for name in renders:
            self.receiver.my_renders.pop(name)
            self.receiver.view.canvas.get_child(name).destroy()

        for name in renders:
            self.receiver.add_model_to_view(name)
            # update canvas so splits happen correctly
            self.receiver.view.canvas.update()

    def undo(self):
        self.receiver.add_model_to_view(self.model_name)

    def __repr__(self):
        return "REMOVED %s FROM VIEW" % self.model_name