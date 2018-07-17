from datastructures import tree

class BSTInsertCommand(object):

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


class BSTRemoveCommand(object):

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


class BSTFindCommand(object):

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        self.receiver = receiver
        self.value = int(value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):

        return self.receiver.find(self.value, change_color=self.change_color)

    def undo(self):
        pass

    def __repr__(self):
        return "FIND %s" % self.value


class BSTRotateCommand(object):
    def __init__(self, receiever, direction, name_a, name_b, should_redraw=True):
        """
        Performs rotation based on direction given and names of nodes.

        :param receiever: BST receiving action
        :param direction: left or right rotation
        :param name_a: variable name as stored in control.my_variables
        :param name_b: variable name as stored in control.my_variables
        :param should_redraw: whether control should redraw after executing
        """
        self.receiver = receiever
        self.direction = direction
        self.name_a = name_a
        self.name_b = name_b
        self.should_redraw = should_redraw

    def execute(self):

        # get variable references from names (may not exist)
        try:
            # node_a = self.receiver.control.my_variables[self.name_a]
            # node_b = self.receiver.control.my_variables[self.name_b]
            node_a = self.receiver.find(int(self.name_a), change_color=False)
            node_b = self.receiver.find(int(self.name_b), change_color=False)

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
            # node_a = self.receiver.control.my_variables[self.name_a]
            # node_b = self.receiver.control.my_variables[self.name_b]
            node_a = self.receiver.find(int(self.name_a), change_color=False)
            node_b = self.receiver.find(int(self.name_b), change_color=False)

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


class CreateBSTCommand(object):
    def __init__(self, receiver, *other_args, should_redraw=True, change_color=True):
        """
        Simply returns a new, empty BST. Optional other args are passed
        to BST constructor.
        Adding receiver as every command uses it and it is passed in
        by command_factory
        """
        self.receiver = receiver
        self.other_args = other_args
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        return tree.BST(*self.other_args)

    def undo(self):
        pass

    def __repr__(self):
        return "CREATE BST"
