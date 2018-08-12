from command import ModelCommand

class BinaryHeapInsertKeyCommand(ModelCommand):

    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        super().__init__()
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

class BinaryHeapRemoveMinCommand(ModelCommand):
    def __init__(self, receiver, should_redraw=True, change_color=True):
        super().__init__()
        self.receiver = receiver
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        return self.receiver.remove_min(change_color=self.change_color)

    def undo(self):
        pass

class BinaryHeapFindCommand(ModelCommand):
    def __init__(self, receiver, value, should_redraw=True, change_color=True):
        super().__init__()
        self.receiver = receiver
        self.value = int(value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        return self.receiver.find(self.value, change_color=self.change_color)

    def undo(self):
        pass

class BinaryHeapDecreaseKeyCommand(ModelCommand):
    def __init__(self, receiver, node_name, new_value, should_redraw=True, change_color=True):
        super().__init__()
        self.receiver = receiver
        self.node_name = node_name
        self.new_value = int(new_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_reference = self.receiver.find(int(self.node_name))
        if node_reference is None:
            raise Exception("No node in heap with value '%s'" % self.node_name)

        self.receiver.decrease_key(node_reference, self.new_value, change_color=self.change_color)

    def undo(self):
        pass