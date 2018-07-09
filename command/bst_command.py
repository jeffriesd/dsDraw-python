

class BSTInsertCommand:

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        """
        Command class for BST. Created by a BSTCommandFactory and passed to
        DrawControl for execution.
        :param receiver: tree object receiving action
        :param value: value being inserted
        :param should_redraw: flag to indicate whether canvas
                            should be repainted upon excecution
        :param change_color: flag to indicate whether nodes
                            should change color during execution
        """
        self.receiver = receiver
        self.value = int(value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        self.receiver.insert(self.value, change_color=self.change_color)

    def undo(self):
        """Current implementation of undo for tree.insert.
            Not perfectly accurate because tree shape may not be same after undo."""
        self.receiver.remove(self.value, change_color=self.change_color)

    def __repr__(self):
        return "INSERT %s" % self.value


class BSTRemoveCommand:

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        self.receiver = receiver
        self.value = int(value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        self.receiver.remove(self.value, change_color=self.change_color)

    def undo(self):
        """Current implementation of undo for tree.remove.
             Not perfectly accurate because tree shape may not be same after undo."""
        self.receiver.insert(self.value, change_color=self.change_color)

    def __repr__(self):
        return "REMOVE %s" % self.value
