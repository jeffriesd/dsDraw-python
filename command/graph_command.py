from command import ModelCommand

class GraphAddNodeCommand(ModelCommand):
    """
    Add a new node and edge from an existing node.

    Accepts integer arguments or node reference for
    from_node.

    e.g. "g.add 5 3"
         "g.add n 3"
    """
    def __init__(self, receiver, from_value, new_value, should_redraw=True, change_color=True):
        super().__init__()      
        self.receiver = receiver
        self.from_value = from_value
        self.new_value = int(new_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_reference = self.get_reference(self.from_value)

        if node_reference is None:
            raise Exception("No node in graph with value '%s'" % self.from_value)

        self.receiver.add_node(node_reference, self.new_value)

    def undo(self):
        pass

class GraphNewNodeCommand(ModelCommand):
    """
    Add a new node without any new edges.
    """
    def __init__(self, receiver, new_value, should_redraw=True, change_color=True):
        super().__init__()
        self.receiver = receiver
        self.new_value = int(new_value)
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        return self.receiver.new_node(self.new_value)

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
        # from_node = self.receiver.find(int(self.from_value))
        from_node = self.get_reference(self.from_value)
        # to_node = self.receiver.find(int(self.to_value))
        to_node = self.get_reference(self.to_value)

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
        self.from_value = from_value
        self.to_value = to_value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        from_node = self.get_reference(self.from_value)
        to_node = self.get_reference(self.to_value)

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
        self.remove_value = remove_value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        node_to_remove = self.get_reference(self.remove_value)
        if node_to_remove is None:
            raise Exception("Can't remove %s: not present" % self.remove_value)
        self.receiver.remove_node(node_to_remove)

    def undo(self):
        pass

class GraphAddOrConnectCommand(ModelCommand):
    """
    Connect to an existing node or create a new
    node and new connecting edge.
    """

    def __init__(self, receiver, from_value, con_value, should_redraw=True, change_color=True):
        super().__init__()
        self.receiver = receiver
        self.from_value = from_value
        self.con_value = con_value
        self.should_redraw = should_redraw
        self.change_color = change_color

    def execute(self):
        """
        Attempt to find value to connect to
        from given node value. If connecting value
        doesn't exist a new node will be created.
        """
        connect_node = self.get_reference(self.con_value)
        if connect_node is None:
            # node doesn't exist, create a new one
            connect_node = self.receiver.new_node(int(self.con_value))

        from_node = self.get_reference(self.from_value)
        self.receiver.create_edge(connect_node, from_node)

    def undo(self):
        pass