
class DSCommand(object):

    def __init__(self):
        """
        Basic command class to set
        some default attributes
        """
        self.receiver = None

        # should graphs be re-assigned coordinates
        self.do_render = True

        # whether to redraw graph to canvas (without necessarily changing coordinates)
        self.should_redraw = True

    def execute(self):
        raise NotImplementedError("Execute not implemented for %s" % self)

    def undo(self):
        raise NotImplementedError("Undo not implemented for %s" % self)


class ModelCommand(DSCommand):

    def __init__(self, change_color=True):
        super().__init__()

        # should animation be shown with color change of nodes
        self.change_color = change_color

    def get_reference(self, arg):
        """
        Parses an argument from the command line.
        If numeric, perform find on receiver.
        If alpha, check control.my_variables
        """
        try:
            int_arg = int(arg)
            return self.receiver.find(int_arg, change_color=self.change_color)
        except ValueError:
            control = self.receiver.control
            return control.my_variables[arg]



