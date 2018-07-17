from time import sleep


class RenderBST(object):
    """
    Wrapper class to handle rendering algorithm (coordinate placement),
    scaling the model to its canvas, drawing to the canvas, handling
    sleeping for animation, because all of these tasks dependent
    upon the type of model.
    """

    def __init__(self, model, canvas, name=None):
        self.model = self.tree = model
        self.canvas = canvas
        self.name = name

        self.tick = .05
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

        if not self.model.root:
            return

        if do_render:
            self.model.render()

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
        # self.logger.debug("entering preprocess stage")
        width = self.canvas.width
        height = self.canvas.height

        self.cell_w = width / (self.tree.max_x - self.tree.min_x + 1)
        self.cell_h = height / (self.tree.max_y - self.tree.min_y + 1)

        # self.logger.debug("cell size set; width: %s, height: %s" % (self.cell_w, self.cell_h))

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

        # traverse tree in preorder so lines get drawn
        # first and nodes are placed on top
        for node in self.tree.preorder():
            x0 = node.x * cell_w
            y0 = node.y * cell_h
            for c in node.children():
                x1 = c.x * cell_w
                y1 = c.y * cell_h
                center_offsets = [cell_w / 2, cell_h / 2] * 2

                pts = [x0, y0, x1, y1]
                centers = [pt + off for pt, off in zip(pts, center_offsets)]

                # show color for bst property
                color = "blue" if c.val <= node.val else "red"
                color = "green" if c.val == node.val else color
                self.canvas.create_line(*centers, fill=color, width=2)

            # draw nodes at 50% size as to not block
            # drawing of edges
            x0_n, y0_n = [x0 + cell_w / 4, y0 + cell_h / 4]

            # self.logger.debug("Drawing Node(%s) at %.2f, %.2f" % (node.val, x0_n, y0_n))

            self.canvas.create_oval(x0_n, y0_n, x0_n + cell_w / 2, y0_n + cell_h / 2, fill=node.color)
            # node_text = ("%sCC:\n%i, %i\ns:%i, d:%i"
            #                               % (node, node.x, node.y,
            #                                  node.get_size(), node.depth))
            # node_text = ("%s\nd: %s; s: %s" % ("   " + str(node), node.depth, node.get_size()))
            # node_text = ("%s\nxl: %s, xr: %s\nd:%s; s:%s" % (node.val, node.xleft.val, node.xright.val, node.depth, node.get_size()))
            node_text = node.val
            # node_text = ""

            self.canvas.create_text(x0 + cell_w / 2, y0 + cell_h / 2,
                                    text=node_text)
