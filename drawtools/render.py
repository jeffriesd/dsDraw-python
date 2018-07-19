from time import sleep


class RenderTree(object):
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

        # used for centering tree on canvas
        self.max_x = -1
        self.max_y = -1

        # minimum separation between nodes
        # on the same level
        self.minsep = 1

        self.tick = .15
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
        width = self.canvas.width
        height = self.canvas.height

        self.cell_w = width / (self.max_x - self.min_x + 1)
        self.cell_h = height / (self.max_y - self.min_y + 1)

        # self.model.logger.debug("cell size set; width: %s, height: %s" % (self.cell_w, self.cell_h))

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

            # self.model.logger.debug("Drawing Node(%s) at %.2f, %.2f" % (node.val, x0_n, y0_n))

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

    def render(self):
        # # Reingold-Tilford algorithm

        self.setup_tr()
        self.petrify_tr()

        # determine max/min x/y
        self.max_x = self.max_y = self.min_x = self.min_y = 0
        for node in self.tree.root:
            self.max_x = max(node.x, self.max_x)
            self.max_y = max(node.y, self.max_y)
            self.min_x = min(node.x, self.min_x)
            self.min_y = min(node.y, self.min_y)

        # temporary fix to place everything on screen
        for node in self.tree.root:
            node.x += abs(self.min_x)

        # print("x: %i, %i; y: %i, %i" % (self.min_x, self.max_x, self.min_y, self.max_y))

    def setup_tr(self):
        """
        Wrapper function for Reingold-Tilford algorithm
        """
        self._setup_tr(self.tree.root, 0, self.tree.root.xleft, self.tree.root.xright)

    def _setup_tr(self, T, depth, rmost, lmost):
        MINSEP = self.minsep
        LL = LR = RL = RR = None

        if T:
            L = T.left
            R = T.right
            LL = L.xleft if L else None
            LR = L.xright if L else None
            RR = R.xright if R else None
            RL = R.xleft if R else None

        CURSEP = ROOTSEP = 0
        LOFFSUM = ROFFSUM = 0

        # base case when past leaves
        if T is None:
            if lmost:
                lmost.depth = -1
            if rmost:
                rmost.depth = -1
            return
        else:
            # T.update_extremes()

            T.y = depth
            # T.depth = depth
            L = T.left
            R = T.right

            self._setup_tr(L, depth + 1, LR, LL)
            self._setup_tr(R, depth + 1, RR, RL)

            self.model.log("debug", "IN TR SETUP: COMPARING %s and %s ; lmost=%s, rmost=%s; ROOT IS %s" % (L, R, lmost, rmost, T),
                        indent=depth)
            self.model.log("debug", "IN TR SETUP: LOFFSUM = %s, ROFFSUM = %s" % (LOFFSUM, ROFFSUM),
                     indent=depth)

            # if T is a leaf
            if not (T.left or T.right):
                self.model.log("debug", "%s is a leaf" % T, indent=depth)
                rmost = T
                lmost = T

                rmost.depth = depth
                lmost.depth = depth
                rmost.root_offset = 0
                lmost.root_offset = 0
                T.par_offset = 0
                self.model.log("debug", "SETTING %s.par_offset = 0" % T, indent=depth)

            else:
                # "superimpose" the subtrees on one another, starting with separation of 0
                CURSEP = MINSEP
                ROOTSEP = MINSEP
                LOFFSUM = 0
                ROFFSUM = 0

                # now consider each level until
                # one subtree is exhausted,
                # pushing apart when necessary
                while L and R:
                    self.model.log("debug", "\n" + ("\t" * depth) + "IN WHILE: L = %s; R = %s; CURSEP = %s" % (L, R, CURSEP),
                             indent=depth)

                    if CURSEP < MINSEP:
                        # push apart
                        push = MINSEP - CURSEP
                        self.model.log("debug", "--- PUSHING APART BY %s" % push,
                                 indent=depth)
                        ROOTSEP += push
                        CURSEP = MINSEP

                    # advance L and R along respective contours
                    if L.right:
                        LOFFSUM += L.par_offset
                        self.model.log("debug", "IN WHILE: LOFFSUM += %s; NOW = %s" % (L.par_offset, LOFFSUM),
                                 indent=depth)

                        self.model.log("debug", "IN WHILE: CURSEP -= L.offset: %s" % L.par_offset,
                                 indent=depth)
                        CURSEP -= L.par_offset

                        self.model.log("debug", "IN WHILE: L -> %s" % L.right,
                                 indent=depth)
                        L = L.right
                    else:
                        LOFFSUM -= L.par_offset
                        self.model.log("debug", "IN WHILE: LOFFSUM -= %s; NOW = %s" % (L.par_offset, LOFFSUM),
                                 indent=depth)

                        self.model.log("debug", "IN WHILE: CURSEP += L.offset: %s" % L.par_offset,
                                 indent=depth)
                        CURSEP += L.par_offset
                        self.model.log("debug", "IN WHILE: L -> %s" % L.left,
                                 indent=depth)
                        L = L.left

                    if R.left:
                        ROFFSUM -= R.par_offset
                        self.model.log("debug", "IN WHILE: ROFFSUM += %s; NOW = %s" % (R.par_offset, ROFFSUM),
                                 indent=depth)

                        self.model.log("debug", "IN WHILE: CURSEP -= R.offset: %s" % R.par_offset,
                                 indent=depth)
                        CURSEP -= R.par_offset
                        self.model.log("debug", "IN WHILE: R -> %s" % R.left,
                                 indent=depth)
                        R = R.left
                    else:
                        ROFFSUM += R.par_offset
                        self.model.log("debug", "IN WHILE: ROFFSUM += %s; NOW = %s" % (R.par_offset, ROFFSUM),
                                 indent=depth)

                        self.model.log("debug", "IN WHILE: CURSEP += R.offset: %s" % R.par_offset,
                                 indent=depth)
                        CURSEP += R.par_offset
                        self.model.log("debug", "IN WHILE: R -> %s" % R.right,
                                 indent=depth)
                        R = R.right

                self.model.log("debug", "WHILE TERMINATED", indent=depth)

                # set the offset in T and include it in
                # accumulated offsets for L and R
                T.par_offset = (ROOTSEP + 1) // 2
                self.model.log("debug", "SETTING %s.par_offset = (ROOTSEP: %s + 1) // 2" % (T, ROOTSEP),
                         indent=depth)
                self.model.log("debug", "SETTING %s.par_offset = %s" % (T, T.par_offset),
                         indent=depth)

                self.model.log("debug", "CURRENT ROOTSEP = %s" % ROOTSEP, indent=depth)

                LOFFSUM -= T.par_offset
                ROFFSUM += T.par_offset
                self.model.log("debug", "LOFFSUM -= %s; NOW = %s" % (T.par_offset, LOFFSUM), indent=depth)
                self.model.log("debug", "ROFFSUM += %s; NOW = %s" % (T.par_offset, ROFFSUM), indent=depth)


                self.model.log("debug", "UPDATING EXTREME DESCENDANTS", indent=depth)
                # update extreme descendants information
                if T.left is None or ((RL and LL) and RL.depth > LL.depth):
                    lmost = RL
                    lmost.root_offset += T.par_offset
                    self.model.log("debug", "%s.root_offset += T.par: %s; NOW = %s" % (lmost, T.par_offset, lmost.root_offset),
                             indent=depth)
                else:
                    lmost = LL

                    # protecting from incrementing root offset twice for
                    # leaf nodes (where rmost and lmost are the same node)
                    if lmost is not rmost:
                        lmost.root_offset -= T.par_offset
                        self.model.log("debug", "%s.root_offset -= T.par: %s; NOW = %s" % (lmost, T.par_offset, lmost.root_offset),
                                 indent=depth)

                self.model.log("debug", "lmost = %s" % lmost, indent=depth)

                # if LR and RR:
                if T.right is None or ((LR and RR) and LR.depth > RR.depth):
                    rmost = LR
                    rmost.root_offset -= T.par_offset
                    self.model.log("debug", "%s.root_offset -= T.par: %s; NOW = %s" % (rmost, T.par_offset, rmost.root_offset),
                             indent=depth)
                else:
                    rmost = RR

                    # protecting from incrementing root offset twice for
                    # leaf nodes (where rmost and lmost are the same node)
                    if lmost is not rmost:
                        rmost.root_offset += T.par_offset
                        self.model.log("debug", "%s.root_offset += T.par: %s; NOW = %s" % (rmost, T.par_offset, rmost.root_offset),
                                 indent=depth)
                self.model.log("debug", "rmost = %s" % rmost, indent=depth)


                self.model.log("debug", "PRE-THREADING: LL = %s, RR = %s, T.par_offset = %s" % (LL, RR, T.par_offset)
                         , indent=depth)
                self.model.log("debug", "PRE-THREADING: L = %s, R = %s, LOFFSUM = %s, ROFFSUM = %s" % (L, R, LOFFSUM, ROFFSUM),
                         indent=depth)
                # if subtrees of T have different heights,
                # check if threading necessary - at most 1 thread
                # will be inserted
                if L and L is not T.left:
                    # create a thread
                    RR.has_thread = True
                    RR.par_offset = abs((RR.root_offset + T.par_offset) - LOFFSUM)
                    self.model.log("debug", "RR.par_offset =  abs((RR.root_offset: %s + T.par_offset) - LOFFSUM)"
                             % RR.root_offset
                             ,indent=depth)
                    self.model.log("debug", "SETTING %s.par_offset = %s" % (RR, RR.par_offset),
                             indent=depth)
                    self.model.log("debug", "THREADING (L) %s to %s" % (RR, L), indent=depth)
                    if LOFFSUM - T.par_offset <= RR.root_offset:
                        RR.left = L
                    else:
                        RR.right = L

                elif R and R is not T.right:
                    # create a thread
                    LL.has_thread = True
                    LL.par_offset = abs((LL.root_offset - T.par_offset) - ROFFSUM)
                    self.model.log("debug", "LL.par_offset = abs((LL.root_offset: %s - T.par_offset) - ROFFSUM)"
                             % LL.root_offset
                             , indent=depth)
                    self.model.log("debug", "SETTING %s.par_offset = %s" % (LL, LL.par_offset),
                             indent=depth)

                    self.model.log("debug", "THREADING (R) %s to %s" % (LL, R), indent=depth)
                    if ROFFSUM + T.par_offset >= LL.root_offset:
                        LL.right = R
                    else:
                        LL.left = R
                self.model.log("debug", "DONE THREADING", indent=depth)

    def petrify_tr(self):
        """Wrapper function for petrify method in
            Reingold-Tilford algorithm -- assigns
            absolute coordinates after setup_tr has
            determined relative placements"""
        self._petrify_tr(self.tree.root, 0)

    def _petrify_tr(self, T, x):
        """Determines absolute coordinates in
            preorder traversal of the tree and
            removes all 'threads' created from setup"""

        if T:
            self.model.log("debug", "IN PETRIFY: T = %s, offset = %s" % (T, T.par_offset))
            T.x = x
            if T.has_thread:
                T.has_thread = False
                T.right = None
                T.left = None
            self._petrify_tr(T.left, x - T.par_offset)
            self._petrify_tr(T.right, x + T.par_offset)


