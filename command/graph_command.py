from command import ModelCommand

class GraphAddNodeCommand(ModelCommand):
    """
    Add a new node and edge from an existing node
    e.g. "g.add 5 3"
    """
    def __init__(self, receiver, from_value, new_value, should_redraw=True, change_color=True):
        super().__init__()      
        self.receiver = receiver
        self.from_value = from_value
        self.new_value = int(new_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_reference = self.receiver.find(int(self.from_value))
        if node_reference is None:
            raise Exception("No node in graph with value '%s'" % self.from_value)

        self.receiver.add_node(node_reference, self.new_value)

    def undo(self):
        pass

class GraphConnectCommand(ModelCommand):
    """
    Create a new edge between two nodes
    e.g. "g.con 5 15"
    """
    def __init__(self, receiver, from_value, to_value, should_redraw=True, change_color=True):
        super().__init__()     
        self.receiver = receiver
        self.from_value = from_value
        self.to_value = to_value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        from_node = self.receiver.find(int(self.from_value))
        to_node = self.receiver.find(int(self.to_value))

        if from_node is None:
            raise Exception("No node in graph with value '%s'" % self.from_value)
        if to_node is None:
            raise Exception("No node in graph with value '%s'" % self.to_value)

        self.receiver.create_edge(from_node, to_node)

    def undo(self):
        pass

class GraphCutCommand(ModelCommand):
    """
    Remove an edge between two nodes
    e.g. g.cut 5 3
    """

    def __init__(self, receiver, from_value, to_value, should_redraw=True, change_color=True):
        super().__init__()      
        self.receiver = receiver
        self.from_value = int(from_value)
        self.to_value = int(to_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        from_node = self.receiver.find(self.from_value)
        to_node = self.receiver.find(self.to_value)

        if from_node is None:
            raise Exception("No node in graph with value '%s'" % self.from_value)
        if to_node is None:
            raise Exception("No node in graph with value '%s'" % self.to_value)

        self.receiver.remove_edge(from_node, to_node)

    def undo(self):
        pass

class GraphRemoveNodeCommand(ModelCommand):
    """
    Remove a node and all its edges.
    """

    def __init__(self, receiver, remove_value, should_redraw=True, change_color=True):
        super().__init__()      
        self.receiver = receiver
        self.remove_value = int(remove_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_to_remove = self.receiver.find(self.remove_value)
        if node_to_remove is None:
            raise Exception("Can't remove %s: not present" % self.remove_value)
        self.receiver.remove_node(node_to_remove)

    def undo(self):
        pass