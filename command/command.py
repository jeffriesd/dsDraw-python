

class InsertCommand:

    def __init__(self, receiver, value, should_redraw=True, change_color=False):
        self.receiver = receiver
        self.value = value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        self.receiver.insert(self.value, change_color=self.change_color)

        # need to pass command state info to controller of the tree
        self.receiver.control.last_command = self

    def undo(self):
        """Current implementation of undo for tree.insert.
            Not perfectly accurate because tree shape may not be same after undo."""
        self.receiver.remove(self.value, change_color=self.change_color)

    def __repr__(self):
        return "INSERT %s" % self.value


class RemoveCommand:

    def __init__(self, receiver, value, should_redraw=True, change_color=False):
        self.receiver = receiver
        self.value = value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        self.receiver.remove(self.value, change_color=self.change_color)
        self.receiver.control.last_command = self

    def undo(self):
        """Current implementation of undo for tree.remove.
             Not perfectly accurate because tree shape may not be same after undo."""
        self.receiver.insert(self.value, change_color=self.change_color)

    def __repr__(self):
        return "REMOVE %s" % self.value
