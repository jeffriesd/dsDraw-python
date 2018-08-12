
class DSCommand(object):

    def __init__(self):
        """
        Basic command class to set
        some default attributes
        """

        # should graphs be re-assigned coordinates
        self.do_render = True

        # whether to redraw graph to canvas (without necessarily changing coordinates)
        self.should_redraw = True


    def execute(self):
        raise NotImplementedError("Execute not implemented for %s" % self)

    def undo(self):
        raise NotImplementedError("Undo not implemented for %s" % self)


class ModelCommand(DSCommand):

    def __init__(self):
        super().__init__()

        # should animation be shown with color change of nodes
        self.change_color = True
