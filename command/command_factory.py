from command.bst_command import BSTInsertCommand, BSTRemoveCommand, BSTFindCommand, \
                                BSTRotateCommand
from command.heap_command import BinaryHeapInsertKeyCommand, BinaryHeapRemoveMinCommand, \
                                 BinaryHeapFindCommand, BinaryHeapDecreaseKeyCommand
from command.control_command import ClearConsoleCommand, CreateVariableCommand, \
                                    PrintVariableCommand, CreateDataStructureCommand, \
                                    ShowRenderCommand, CloseRenderCommand, \
                                    CreateSequenceCommand
from command.graph_command import GraphAddNodeCommand, GraphConnectCommand, GraphCutCommand, \
                                    GraphRemoveNodeCommand, GraphAddOrConnectCommand, GraphNewNodeCommand
from command.sequence_command import SequenceExecuteCommand
from util.exceptions import InvalidCommandError


class CommandFactory(object):
    def __init__(self):
        self.receiver = None
        self.command_list = {}

    def create_command(self, type, *args, **kwargs):
        """Create a new command object with given arguments (logical arguments
                    from command prompt) and keyword args for meta-information
                    like whether to redraw after executing or whether to show color for animation"""

        # if command is invalid, return None. This will be propagated back to
        # the view class and interpreted as a syntax error
        try:
            my_command = self.command_list[type]
            return my_command(self.receiver, *args, **kwargs)
        except KeyError:
            raise InvalidCommandError("Invalid command for %s: '%s'" % (self.receiver, type))
        except ValueError:
            raise InvalidCommandError("Invalid arguments for '%s': '%s'" % (type, args))

class ControlCommandFactory(CommandFactory):
    """
    Class to instantiate commands with control object
    as receiver. These include commands for clearing the console,
    and assigning variable names to returned references.
    """
    def __init__(self, receiver):
        self.receiver = receiver

        self.command_list = {
            "clear": ClearConsoleCommand,
            "assign": CreateVariableCommand,
            "print": PrintVariableCommand,
            "create": CreateDataStructureCommand,
            "show": ShowRenderCommand,
            "close": CloseRenderCommand,
            "sequence": CreateSequenceCommand,
        }


class BSTCommandFactory(CommandFactory):
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
            "remove": BSTRemoveCommand,
            "find": BSTFindCommand,
            "rotate": BSTRotateCommand
        }


class BinaryHeapCommandFactory(CommandFactory):
    """Class to instantiate command objects for BinaryHeap.
    Call get_command_factory() from a heap object
    to get an instance of BinaryHeapCommandFactory"""

    def __init__(self, receiver):
        self.receiver = receiver

        self.command_list = {
            "insert": BinaryHeapInsertKeyCommand,
            "find": BinaryHeapFindCommand,
            "r-min": BinaryHeapRemoveMinCommand,
            "dec": BinaryHeapDecreaseKeyCommand
        }


class GraphCommandFactory(CommandFactory):
    """
    Class to instantiate command objects for Graph.
    """
    def __init__(self, receiver):
        self.receiver = receiver
        self.command_list = {
            "add": GraphAddNodeCommand,
            "con": GraphConnectCommand,
            "cut": GraphCutCommand,
            "remove": GraphRemoveNodeCommand,
            "new": GraphNewNodeCommand,
            "conadd": GraphAddOrConnectCommand,
        }


class SequenceCommandFactory(CommandFactory):

    def __init__(self, receiver):
        self.receiver = receiver
        self.command_list = {
            "execute": SequenceExecuteCommand,
        }

