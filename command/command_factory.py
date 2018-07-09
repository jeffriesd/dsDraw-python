from command.bst_command import BSTInsertCommand, BSTRemoveCommand
from util.exceptions import InvalidCommandError

class BSTCommandFactory(object):
    """Class to instantiate command objects for BST.
        Call get_command_factory() from a bst object
        to get an instance of BSTCommandFactory"""

    def __init__(self, receiver):
        """
        Initializes receiver and list of valid commands for this factory.
        :param receiver: object command is being performed upon
        """

        self.receiver = receiver

        self.command_list = {
            "insert": BSTInsertCommand,
            "remove": BSTRemoveCommand
        }

    def create_command(self, type, *args, **kwargs):
        """Create a new command object with given arguments (logical arguments
            from command prompt) and keyword args for meta-information
            like whether to redraw after executing or whether to show color for animation"""

        # if command is invalid, return None. This will be propagated back to
        # the view class and interpreted as a syntax error
        try:
            my_command = self.command_list[type.lower()]
            return my_command(self.receiver, *args, **kwargs)
        except KeyError:
            raise InvalidCommandError("Invalid command for BST: '%s'" % type)

