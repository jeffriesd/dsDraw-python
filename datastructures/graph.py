from time import sleep
import random
import logging
import util.logging_util as log
from util.my_threads import LoopThread
from command.command_factory import GraphCommandFactory
from datastructures.basic import DataStructure
from functools import partial
from threading import Thread
from math import tanh

class GraphNode(object):
    def __init__(self, value, x=0, y=0):
        self.val = value
        self.x = x
        self.y = y

        self.dx = 0
        self.dy = 0

        self.color = "white"

    def __repr__(self):
        return "GraphNode(%s)" % self.val

    def __int__(self):
        return self.val

class Graph(DataStructure):
    def __init__(self, prebuild_size = 0, name=None):
        self.name = name

        self.nodes = []
        self.edges = []

        if prebuild_size:

            def build_tree(size):
                for i in range(size):
                    if i == 0:
                        self.nodes.append(GraphNode(i))
                    else:
                        parent = self.nodes[i // 2]
                        self.add_node(parent, i)
            # build_tree(int(prebuild_size))
            og = GraphNode(-11)
            self.nodes.append(og)
            for i in range(int(prebuild_size)):
            #     # from_value = random.choice(self.nodes)
            #     # from_value = self.nodes[-1]
            #     # new = self.add_node(from_value, i)
                new = self.add_node(og, i)
            #     #
                # # fully connected
                for v in self.nodes:
                # rn = random.randint(0, len(self.nodes))
                # for v in random.sample(self.nodes, rn):
                    if v is not new:
                        self.create_edge(v, new)

                # create ring
            # self.create_edge(self.nodes[0],self.nodes[-1])

    def __repr__(self):
        return "Graph structure with %s nodes" % len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def get_command_factory(self):
        return GraphCommandFactory(self)

    def get_render_class(self):
        return RenderGraph

    def add_node(self, from_node, value):
        """
        Creates a new node and edge
        :param from_node: reference to GraphNode
        :param value: value of new node
        :return: new GraphNode connected to from_node
        """
        n = len(self.nodes)
        x = random.randint(-n, n)
        y = random.randint(-n, n)

        new_node = GraphNode(value, x=x, y=y)
        self.nodes.append(new_node)

        self.create_edge(from_node, new_node)
        return new_node

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
            same_val = list(filter(lambda n: n.val == value, self.nodes))
            return same_val[0]
        except IndexError:
            return None


class RenderGraph(object):
    def __init__(self, model, canvas, name=None):
        self.model = self.graph = model
        self.canvas = canvas
        self.name = name

        # used for centering graph on canvas
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0

        self.tick = 0.02
        self.focused = False

    def display(self, do_render=True, do_sleep=False):
        """Renders data structure (preprocess),
            clears canvas, and draws to canvas
            :param do_render - flag whether to run render algorithm again or not
            :param do_sleep - flag whether to pause for animation purposes or not"""

        # show focus with bg color
        if self.focused:
            self.canvas.configure(bg="#ddd")
        else:
            self.canvas.configure(bg="#aaa")

        if not self.graph.nodes:
            return

        if do_render:
            # rt = TestThread(target=self.render, sleep_time=self.tick)
            # rt = Thread(target=self.render)
            # rt.start()
            self.render()

        # determine node sizes
        self.preprocess()

        self.clear_canvas()
        self.draw_on_canvas()

        if do_sleep:
            self.canvas.update()
            sleep(self.tick)

    def clear_canvas(self):
        self.canvas.delete("all")

    def preprocess(self):
        """Determines actual size of each node.
            Called after tree.render() because value
            ranges needed for x and y"""
        # self.model.logger.debug("entering preprocess stage")
        # determine max/min x/y
        xs = [v.x for v in self.graph.nodes]
        ys = [v.y for v in self.graph.nodes]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)

        # print("min, max, x, y: %s %s %s %s" % (self.min_x, self.min_y, self.max_x, self.max_y))

        # x_scale = (self.max_x - self.min_x)

        # temporary fix to place everything on screen
        for node in self.graph.nodes:
            node.x -= (self.min_x)
            node.y -= (self.min_y)


        width = self.canvas.width
        height = self.canvas.height

        self.cell_w = width / (self.max_x - self.min_x + 1)
        self.cell_h = height / (self.max_y - self.min_y + 1)

        self.model.logger.debug("cell size set; width: %s, height: %s" % (self.cell_w, self.cell_h))

    def draw_on_canvas(self, circle=False):
        """
               Determines size of each cell to be drawn and
               iterates through tree, drawing edges first, then
               nodes in an inorder traversal.
               :param circle: if True, draw nodes as circles
               """
        # show name in top left corner
        self.canvas.create_text(5, 5, text=self.name, anchor="nw")

        # if circle set to True, then
        # pick smaller of width/height
        if circle:
            cell_w = cell_h = min(self.cell_w, self.cell_h)
        else:
            cell_w = self.cell_w
            cell_h = self.cell_h


        # draw edges first
        for u, v in self.graph.edges:
            x0 = u.x * cell_w
            y0 = u.y * cell_h
            x1 = v.x * cell_w
            y1 = v.y * cell_h
            center_offsets = [cell_w / 2, cell_h / 2] * 2

            pts = [x0, y0, x1, y1]
            centers = [pt + off for pt, off in zip(pts, center_offsets)]

            color = "black"
            self.canvas.create_line(*centers, fill=color, width=2)

        for node in self.graph.nodes:
            x0 = node.x * cell_w
            y0 = node.y * cell_h

            # # draw nodes at 50% size as to not block
            # # drawing of edges
            # x0_n, y0_n = [x0 + cell_w / 4, y0 + cell_h / 4]
            #
            # # self.model.logger.debug("Drawing Node(%s) at %.2f, %.2f" % (node.val, x0_n, y0_n))
            #
            # self.canvas.create_oval(x0_n, y0_n, x0_n + cell_w / 2, y0_n + cell_h / 2, fill=node.color)

            # draw nodes at 50% size as to not block
            # drawing of edges
            x0_n, y0_n = [x0 + 4 * cell_w / 10, y0 + 4 * cell_h / 10]

            # self.model.logger.debug("Drawing Node(%s) at %.2f, %.2f" % (node.val, x0_n, y0_n))

            self.canvas.create_oval(x0_n, y0_n, x0_n + 2 * cell_w / 10, y0_n + 2 * cell_h / 10, fill=node.color)


            node_text = node.val

            self.canvas.create_text(x0 + cell_w / 2, y0 + cell_h / 2,
                                    text=node_text)
            
    def move_nodes(self):

        width = self.canvas.width
        height = self.canvas.height

        for v in self.graph.nodes:
            # repulse all nodes from each other
            r_x = 0
            r_y = 0

            for u in self.graph.nodes:
                if u is not v:
                    x, y, = self.force_r(u, v)
                    r_x += x
                    r_y += y
            # print("total repulsive force on u = %s" % r_x)

            # attract connected nodes
            a_x = 0
            a_y = 0
            for _u, _v in self.graph.edges:
                if v is _u:
                    x, y, = self.force_a(_v, _u)
                    a_x += x
                    a_y += y
                elif v is _v:
                    x, y = self.force_a(_u, _v)
                    a_x += x
                    a_y += y

            # print("total attractive force: %s" % a_x)

            f_x = r_x + a_x
            f_y = r_y + a_y

            v.dx = f_x
            v.dy = f_y

        for v in self.graph.nodes:
            scaled_fx = self.temp * v.dx
            scaled_fy = self.temp * v.dy
            v.x += scaled_fx
            v.y += scaled_fy

            # pull towards 0,0 ?
            try:
                d_to_origin = (v.x ** 2 + v.y**2) ** .5
                scale_factor = .9995 ** d_to_origin
            except OverflowError:
                scale_factor = 0.0000001

            v.x *= scale_factor
            v.y *= scale_factor


        self.preprocess()
        self.clear_canvas()
        self.draw_on_canvas()
        self.canvas.update()

        # cooling
        self.temp *= .9995


    def force_r(self, u, v):
        r_constant = 1

        dx = v.x - u.x
        dy = v.y - u.y

        norm = (dx ** 2 + dy ** 2) ** .5
        norm = .1 if norm == 0 else norm

        unit_x = dx / norm
        unit_y = dy / norm

        r_x = (r_constant / norm ** 2) * unit_x
        r_y = (r_constant / norm ** 2) * unit_y

        # print("repulsion on (%.3f, %.3f) from (%.3f, %.3f): %.3f, %.3f" % (u.x, u.y, v.x, v.y, r_x, r_y))
        # print("repulsion = %.3f, %.3f" % (r_x, r_y))
        return r_x, r_y

    def force_a(self, u: GraphNode, v: GraphNode) -> (float, float):
        a_constant = 1
        spring_length = 1

        dx = v.x - u.x
        dy = v.y - u.y

        norm = (dx ** 2 + dy ** 2) ** .5
        norm = .1 if norm == 0 else norm

        unit_x = dx / norm
        unit_y = dy / norm

        a_x = -a_constant * (norm - spring_length) * unit_x
        a_y = -a_constant * (norm - spring_length) * unit_y

        # print("attraction = %.3f, %.3f" % (a_x, a_y), end="")
        # print(" ; from (%.1f, %.1f) to (%.1f, %.1f)" % (u.x, u.y, v.x, v.y))

        return a_x, a_y

    def render(self, iterations=150):
        """
        Determine coordinates of nodes
        for placement on canvas

        Initialized to random coordinates in
        [-|V|^2 , |V|^2] range

        Moving of nodes through simulated forces is
        handled in a separate thread so each iteration
        can be displayed while other tasks go on.

        (modeled after Fruchterman and Reingold algorithm)
        """

        n = len(self.graph.nodes)
        # randomly initialize node placement
        for v in self.graph.nodes:
            # dont allow duplicate
            other_coords = [(u.x, u.y) for u in self.graph.nodes if u is not v]
            while (v.x, v.y) in other_coords:
                v.x = random.randint(-n, n)
                v.y = random.randint(-n, n)


        # # temperature constant determines how far nodes can
        # # move in each iteration
        self.temp = .02

        # create a new thread to handle moving nodes with
        # simulated forces of attraction/repulsion
        simulation_thread = LoopThread(target=self.move_nodes, n_iter=iterations, sleep_time=self.tick)
        simulation_thread.start()




