class BinaryHeapInsertKeyCommand(object):

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        self.receiver = receiver
        self.value = int(value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        return self.receiver.insert_key(self.value, change_color=self.change_color)

    def undo(self):
        pass

    def __repr__(self):
        return "INSERT KEY %s" % self.value