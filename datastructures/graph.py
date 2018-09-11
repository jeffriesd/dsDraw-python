import random
from command.command_factory import GraphCommandFactory
from datastructures.basic import DataStructure
from drawtools.render import RenderGraph
import datastructures.interactive


class GraphNode(object):
    def __init__(self, value, x=0, y=0):
        self.value = value
        self.x = x
        self.y = y

        self.dx = 0
        self.dy = 0

        # keep track of ID so nodes can be moved
        # instead of deleting/redrawing every time
        self.tk_id = None

        self.color = "white"

    def __repr__(self):
        return "GraphNode(%s)" % self.value
    def __int__(self):
        return self.value

class Graph(DataStructure):
    def __init__(self, prebuild_size = 0, name=None):
        self.name = name

        self.nodes = []
        self.edges = []

        if prebuild_size:

            og = GraphNode(-11)
            self.nodes.append(og)
            for i in range(int(prebuild_size)):
                new = self.new_node(i)

                # # fully connected
                for v in self.nodes:
                    if v is not new:
                        self.create_edge(v, new)

    def __repr__(self):
        return "Graph structure with %s nodes" % len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def clone(self):
        """
        Deep copy graph by copying
        node values and coordinates
        :return:
        """
        clone = Graph()
        for node in self.nodes:
            clone.nodes.append(GraphNode(value=node.value, x=node.x, y=node.y))

        for u, v in self.edges:
            u_clone = clone.find(u.value)
            v_clone = clone.find(v.value)
            clone.create_edge(u_clone, v_clone)


    def get_command_factory(self):
        return GraphCommandFactory(self)

    def get_render_class(self):
        return RenderGraph

    def get_interactive_class(self):
        return datastructures.interactive.InteractiveGraph

    def add_node(self, from_node, value):
        """
        Creates a new node and edge
        :param from_node: reference to GraphNode
        :param value: value of new node
        :return: new GraphNode connected to from_node
        """
        new_node = self.new_node(value)

        self.create_edge(from_node, new_node)
        return new_node

    def new_node(self, value):
        n = len(self.nodes)
        x = random.randint(-n, n)
        y = random.randint(-n, n)

        new = GraphNode(value, x=x, y=y)
        self.nodes.append(new)
        return new

    def remove_node(self, node_to_remove):
        if node_to_remove in self.nodes:
            edges = [(u, v) for u, v in self.edges if node_to_remove in [u, v]]
            for e in edges:
                self.edges.remove(e)
            self.nodes.remove(node_to_remove)
        else:
            raise Exception("Cant' remove %s: not present" % node_to_remove)

    def create_edge(self, from_node, to_node):
        self.edges.append((from_node, to_node))

    def remove_edge(self, from_node, to_node):
        """
        Edge may appear reversed
        """
        try:
            self.edges.remove((from_node, to_node))
            return
        except ValueError:
            pass
        try:
            self.edges.remove((to_node, from_node))
            return
        except ValueError:
            pass

        raise Exception("Edge pair (%s, %s) not present" % (from_node, to_node))

    def find(self, value, change_color=False):
        try:
            same_val = list(filter(lambda n: n.value == value, self.nodes))
            return same_val[0]
        except IndexError:
            return None





