
class ClearConsoleCommand(object):
    def __init__(self, receiver, should_redraw=False):
        """
        Command class for Control object. Created by a ControlCommandFactory and passed to
        DrawControl for execution.
        :param receiver: control object receiving action
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
    pass
