from datastructures import tree
from command import ModelCommand

class BSTInsertCommand(ModelCommand):

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
        super().__init__()
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


class BSTRemoveCommand(ModelCommand):

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        super().__init__()
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


class BSTFindCommand(ModelCommand):

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        super().__init__()         
        self.receiver = receiver
        self.value = value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_ref = self.get_reference(self.value)

        # if self.value is a reference and not an int
        try:
            int_val = int(self.value)
        except ValueError:
            node_ref = self.receiver.find(node_ref.value, change_color=self.change_color)

        return node_ref

    def undo(self):
        pass

    def __repr__(self):
        return "FIND %s" % self.value


class BSTRotateCommand(ModelCommand):
    def __init__(self, receiever, direction, name_a, name_b, should_redraw=True):
        """
        Performs rotation based on direction given and names of nodes.

        :param receiever: BST receiving action
        :param direction: left or right rotation
        :param name_a: variable name as stored in control.my_variables
        :param name_b: variable name as stored in control.my_variables
        :param should_redraw: whether control should redraw after executing
        """
        super().__init__()
        self.receiver = receiever
        self.direction = direction
        self.name_a = name_a
        self.name_b = name_b
        self.should_redraw = should_redraw
        self.change_color = False

    def execute(self):

        # get variable references from names (may not exist)
        try:
            node_a = self.get_reference(self.name_a)
            node_b = self.get_reference(self.name_b)

            if self.direction == "left":
                self.receiver.rotate_left(node_a, node_b)
            elif self.direction == "right":
                self.receiver.rotate_right(node_a, node_b)
            else:
                raise ValueError("No such command")

        except KeyError as e:
            raise KeyError("Reference could not be resolved: %s" % e)

    def undo(self):
        # get variable references from names (may not exist)
        try:
            node_a = self.get_reference(self.name_a)
            node_b = self.get_reference(self.name_b)

            if self.direction == "right":
                self.receiver.rotate_left(node_b, node_a)
            elif self.direction == "left":
                self.receiver.rotate_right(node_b, node_a)
            else:
                raise ValueError("No such command")

        except KeyError as e:
            raise KeyError("Reference could not be resolved: %s" % e)

    def __repr__(self):
        return "%s ROTATE %s, %s" % (self.direction.upper(), self.name_a, self.name_b)

