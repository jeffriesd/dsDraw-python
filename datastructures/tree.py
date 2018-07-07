from datastructures import graph
from collections import defaultdict
from util import logging_util as log
import math
from copy import copy
import logging
from time import sleep
from command.command_factory import BSTCommandFactory


class TreeNode:
    def __init__(self, val, depth=0, parent=None,
                 left=None, right=None, xleft=None, xright=None):
        """
        TreeNode class
        :param val: value stored in node -- currently only using ints
        :param depth: depth from root of tree -- updated at insert time
        :param parent: reference to parent node
        :param left: reference to left child
        :param right: reference to right child
        :param xleft: extreme left descendant (leftmost node in bottom layer of subtree)
        :param xright: extreme right descendant
        :param par_offset: horizontal offset from this node to parent
        :param root_offset: horizontal offset from this node to root
        """
        self.val = val
        self.parent = parent
        self.left = left
        self.right = right

        # a subtree consisting of a single node
        # is its own extreme descendant
        self.xleft = xleft if xleft else self
        self.xright = xright if xright else self

        # used in Reingold-Tilford algorithm
        self.has_thread = False

        self.depth = depth
        self.x = -1
        self.y = -1
        self.shift = 0
        self.size = 1
        self.par_offset = 0
        self.root_offset = 0

        self.color = 'white'

    def __repr__(self):
        return str(self.val)

    def __eq__(self, other):
        return self.val == other.val

    def __lt__(self, other):
        return self.val < other.val

    def __gt__(self, other):
        return self.val > other.val

    def __le__(self, other):
        return self.val <= other.val

    def __ge__(self, other):
        return self.val >= other.val

    def __iter__(self):
        """Inorder traversal"""
        if self.left_child():
            for node in self.left_child():
                yield node
        yield self
        if self.right_child():
            for node in self.right_child():
                yield node

    def preorder(self):
        yield self
        if self.left_child():
            for node in self.left_child().preorder():
                yield node
        if self.right_child():
            for node in self.right_child().preorder():
                yield node

    def postorder(self):
        if self.left_child():
            for node in self.left_child().postorder():
                yield node
        if self.right_child():
            for node in self.right_child().postorder():
                yield node
        yield self

    def children(self):
        """Returns list of children if any exist"""
        return [n for n in [self.left, self.right] if n is not None]

    def left_child(self):
        return self.left

    def right_child(self):
        return self.right

    def is_leaf(self):
        return not self.left and not self.right

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size

    def inc_size(self):
        self.set_size(self.size + 1)

    def dec_size(self):
        self.set_size(self.size - 1)

    def update_size(self):
        self.size = sum(t.size for t in self.children()) + 1

    def get_extremes(self):
        return [self.xleft, self.xright]

    def update_extremes(self):
        if self.is_leaf():
            self.xleft = self
            self.xright = self
            return

        child_extremes = [x for c in self.children()
                          for x in c]

        # get max depth
        max_d = max([x.depth for x in child_extremes])

        deepest = list(filter(lambda n: n.depth == max_d, child_extremes))

        self.xleft = min(deepest)
        self.xright = max(deepest)


    def get_min(self):
        """Recursive method to get minimum
            descendant in O(logn) time"""
        if not self.left_child():
            return self
        if self.left_child():
            return self.left.get_min()

    def get_max(self):
        """Recursive method to get maximum
            descendant in O(logn) time"""
        if not self.right_child():
            return self
        if self.right_child():
            return self.right.get_max()

    def successor(self):
        """Returns inorder successor of node. Two cases.
            1. cur_node has a right child, pick the left most child of it
            2. cur_node has no right child. Traverse parent nodes until traversal
               takes a step to the right"""
        if self.right_child():
            return self.right.get_min()
        else:
            node = self
            parent = node.parent
            while parent and node is not parent.left:
                node = parent
                parent = node.parent
            return node

    def predecessor(self):
        """Returns inorder predecessor of node. Two cases.
            1. cur_node has a left child, pick the right most child of it
            2. cur_node has no left child. Traverse parent nodes until traversal
                takes a step to the left"""
        if self.left_child():
            return self.left.get_max()
        else:
            node = self
            parent = node.parent
            while parent and node is not parent.right:
                node = parent
                parent = node.parent
            return node

    def pred_or_succ(self):
        """Returns predecessor or successor of current node,
            whichever one is a leaf (for easy removal)"""
        if self.left_child():
            return self.predecessor()
        elif self.right_child():
            return self.successor()
        # pred = self.predecessor()
        # succ = self.successor()
        # if pred.is_leaf():
        #     return pred
        # elif succ.is_leaf():
        #     return succ
        return None

    def is_left_child(self):
        return self is self.parent.left


class BST:
    """
    Binary search tree class. Keeps track of size,
    height of tree (max_depth), and maintains a reference
    to root TreeNode
    :param root -- root of tree
    :param minsep -- used for minimum separation in Reingold-Tilford algorithm
    """
    def __init__(self, root=None, minsep=1):
        self.root = root
        self.max_depth = 0
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
        self.size = 0
        self.minsep = minsep

    def __repr__(self):
        return "BST with root %s" % self.root

    def set_control(self, control):
        """Sets reference for controller"""
        self.control = control

    def set_logger(self, logger):
        self.logger = logger
        self.clear_log()
        self.log("info", "\n\n\t----- new run -----\n")

        # excluding debug information
        self.log("info", "setting level to info")
        self.logger.setLevel(logging.INFO)

    def clear_log(self):
        with open('../logs/model_log.log', 'w') as _:
            pass

    def log(self, level_str, message, indent=0):
        """
        Wrapper function for logging -- data structure may be created
        before the control object (and thus the logger) has been initialized
        :param level_str: string specifying logging level
        :param message: message to log
        :return:
        """

        message = "\t" * indent * 1 + message
        try:
            if self.logger:
                log_func = log.to_function(self.logger, level_str)
                log_func(message)
        except AttributeError:
            pass
            # print("no logger ; message was %s" % message)

    def get_command_factory(self):
        """Return appropriate command factory for BST"""
        return BSTCommandFactory(self)

    def insert(self, el, change_color=False):
        """
        Wrapper method to call recursive insert.
        :param el: element being inserted
        :param change_color: shows traversal of tree for visual purposes
        """
        self.log("info", "calling wrapper insert func with root %s to insert %i" % (self.root, el))
        if self.root:
            self.root = self._insert(self.root, el, 0, change_color)
        else:
            self.root = TreeNode(el)

        self.size += 1

    def _insert(self, cur_node, el, depth, change_color):
        """
        Recursive insert function
        :param cur_node: current working node
        :param el: value being inserted
        :param depth: current depth in tree
        :param change_color: shows traversal of tree for visual purposes
        """

        self.log("debug", "inserting %i at depth %i" % (el, depth))

        # change color to show traversal of tree
        if change_color:
            cur_node.color = 'red'
            self.control.display(do_render=False, do_sleep=True)
            cur_node.color = 'white'

        # update depth
        if depth > self.max_depth:
            self.max_depth = depth

        if el <= cur_node.val:
            self.log("debug", "%i <= %i; going left" % (el, cur_node.val))
            if cur_node.left:
                cur_node.left = self._insert(cur_node.left, el, depth+1, change_color)
            else:
                self.log("debug", "new leaf (%s) inserted at depth %i" % (el, depth+1))
                cur_node.left = TreeNode(el, depth=depth+1, parent=cur_node)
        else:
            self.log("debug", "%i > %i; going right" % (el, cur_node.val))
            if cur_node.right:
                cur_node.right = self._insert(cur_node.right, el, depth+1, change_color)
            else:
                self.log("debug", "new leaf (%s) inserted at depth %i" % (el, depth+1))
                cur_node.right = TreeNode(el, depth=depth+1, parent=cur_node)

        # update size
        cur_node.inc_size()

        # update extreme descendants
        cur_node.update_extremes()

        return cur_node

    def remove(self, el, change_color=False):
        """Wrapper method for recursive remove method"""
        self.log("info", "calling wrapper remove func with root %s to remove %i" % (self.root, el))

        if self.find(el):
            # if tree has exactly one node
            if self.root.size == 1:
                self.root = None
            else:
                self.root = self._remove(self.root, el, change_color)
                self.root.update_size()
        else:
            raise Exception("Can't remove %s. Not present in tree" % el)

    def _remove(self, cur_node, el, change_color):
        """Recursive remove method. Three possible cases:
            1. cur_node is leaf, simply remove it
            2. cur_node has one child, simply swap and remove
            3. cur_node has two children. Find successor of cur_node,
               swap with cur_node and then delete cur_node from its new position"""
        if cur_node is None:
            return

        # change color of current node to show traversal of tree
        if change_color:
            cur_node.color = 'red'
            self.control.display(do_render=True, do_sleep=True)
            cur_node.color = 'white'

        if el == cur_node.val:
            # case 1
            if cur_node.is_leaf():
                return None
            # case 2
            elif cur_node.size == 2:
                # swap with child (only need to swap values)
                child = cur_node.children()[0]
                cur_node = self._remove(cur_node, child.val, change_color)
                cur_node.val = child.val
            # case 3
            else:
                # pick predecessor or successor (chosen in that order)
                ps = cur_node.pred_or_succ()
                if ps:
                    # swap value with pred/succ
                    pval = ps.val
                    ps.val = cur_node.val
                    cur_node.val = pval

                    # now that node to be removed has been swapped,
                    # remove it (first determine if it is a left or right child)
                    if ps.is_left_child():
                        ps.parent.left = self._remove(ps, ps.val, change_color)
                    else:
                        ps.parent.right = self._remove(ps, ps.val, change_color)

                    # update extreme descendant information
                    ps.parent.update_extremes()

                    # when final swap happens, make O(log n) traversal
                    # back up to root to update sizes
                    if ps.is_leaf():
                        node = ps.parent
                        while node:
                            node.dec_size()
                            node = node.parent

        # recurse left or right
        elif el < cur_node.val:
            cur_node.left = self._remove(cur_node.left, el, change_color)
        elif el > cur_node.val:
            cur_node.right = self._remove(cur_node.right, el, change_color)

        cur_node.update_size()
        cur_node.update_extremes()

        return cur_node

    def find(self, el):
        """Wrapper method for recursive find function"""
        return self._find(self.root, el)

    def _find(self, cur_node, el):
        """Standard recursive find method O(logn)"""
        if cur_node.val == el:
            return cur_node

        if cur_node.is_leaf():
            return None

        if el <= cur_node.val:
            return self._find(cur_node.left, el)
        else:
            return self._find(cur_node.right, el)


    def print_inorder(self, coords=False):
        """
        Wrapper to call recursive function.
        coords designates whether to print coordinates
        as well as node values
        """
        self._print_inorder(self.root, coords)

    def _print_inorder(self, node, coords):
        """
        Recursive function to print tree in sorted ordering.
        """
        if node is None:
            return
        self._print_inorder(node.left, coords)
        if coords:
            print("(%s: x = %i, y = %i)" % (node, node.x, node.y))
        else:
            print(node, end=" ")
        self._print_inorder(node.right, coords)

    def setup_tr(self):
        """
        Wrapper function for Reingold-Tilford algorithm
        """
        self._setup_tr(self.root, 0, self.root.xleft, self.root.xright)

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

            self.log("debug", "IN TR SETUP: COMPARING %s and %s ; lmost=%s, rmost=%s; ROOT IS %s" % (L, R, lmost, rmost, T),
                        indent=depth)
            self.log("debug", "IN TR SETUP: LOFFSUM = %s, ROFFSUM = %s" % (LOFFSUM, ROFFSUM),
                     indent=depth)

            # if T is a leaf
            if not (T.left or T.right):
                self.log("debug", "%s is a leaf" % T, indent=depth)
                rmost = T
                lmost = T

                rmost.depth = depth
                lmost.depth = depth
                rmost.root_offset = 0
                lmost.root_offset = 0
                T.par_offset = 0
                self.log("debug", "SETTING %s.par_offset = 0" % T, indent=depth)

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
                    self.log("debug", "\n" + ("\t" * depth) + "IN WHILE: L = %s; R = %s; CURSEP = %s" % (L, R, CURSEP),
                             indent=depth)

                    if CURSEP < MINSEP:
                        # push apart
                        push = MINSEP - CURSEP
                        self.log("debug", "--- PUSHING APART BY %s" % push,
                                 indent=depth)
                        ROOTSEP += push
                        CURSEP = MINSEP

                    # advance L and R along respective contours
                    if L.right:
                        LOFFSUM += L.par_offset
                        self.log("debug", "IN WHILE: LOFFSUM += %s; NOW = %s" % (L.par_offset, LOFFSUM),
                                 indent=depth)

                        self.log("debug", "IN WHILE: CURSEP -= L.offset: %s" % L.par_offset,
                                 indent=depth)
                        CURSEP -= L.par_offset

                        self.log("debug", "IN WHILE: L -> %s" % L.right,
                                 indent=depth)
                        L = L.right
                    else:
                        LOFFSUM -= L.par_offset
                        self.log("debug", "IN WHILE: LOFFSUM -= %s; NOW = %s" % (L.par_offset, LOFFSUM),
                                 indent=depth)

                        self.log("debug", "IN WHILE: CURSEP += L.offset: %s" % L.par_offset,
                                 indent=depth)
                        CURSEP += L.par_offset
                        self.log("debug", "IN WHILE: L -> %s" % L.left,
                                 indent=depth)
                        L = L.left

                    if R.left:
                        ROFFSUM -= R.par_offset
                        self.log("debug", "IN WHILE: ROFFSUM += %s; NOW = %s" % (R.par_offset, ROFFSUM),
                                 indent=depth)

                        self.log("debug", "IN WHILE: CURSEP -= R.offset: %s" % R.par_offset,
                                 indent=depth)
                        CURSEP -= R.par_offset
                        self.log("debug", "IN WHILE: R -> %s" % R.left,
                                 indent=depth)
                        R = R.left
                    else:
                        ROFFSUM += R.par_offset
                        self.log("debug", "IN WHILE: ROFFSUM += %s; NOW = %s" % (R.par_offset, ROFFSUM),
                                 indent=depth)

                        self.log("debug", "IN WHILE: CURSEP += R.offset: %s" % R.par_offset,
                                 indent=depth)
                        CURSEP += R.par_offset
                        self.log("debug", "IN WHILE: R -> %s" % R.right,
                                 indent=depth)
                        R = R.right

                self.log("debug", "WHILE TERMINATED", indent=depth)

                # set the offset in T and include it in
                # accumulated offsets for L and R
                T.par_offset = (ROOTSEP + 1) // 2
                self.log("debug", "SETTING %s.par_offset = (ROOTSEP: %s + 1) // 2" % (T, ROOTSEP),
                         indent=depth)
                self.log("debug", "SETTING %s.par_offset = %s" % (T, T.par_offset),
                         indent=depth)

                self.log("debug", "CURRENT ROOTSEP = %s" % ROOTSEP, indent=depth)

                LOFFSUM -= T.par_offset
                ROFFSUM += T.par_offset
                self.log("debug", "LOFFSUM -= %s; NOW = %s" % (T.par_offset, LOFFSUM), indent=depth)
                self.log("debug", "ROFFSUM += %s; NOW = %s" % (T.par_offset, ROFFSUM), indent=depth)


                self.log("debug", "UPDATING EXTREME DESCENDANTS", indent=depth)
                # update extreme descendants information
                if T.left is None or ((RL and LL) and RL.depth > LL.depth):
                    lmost = RL
                    lmost.root_offset += T.par_offset
                    self.log("debug", "%s.root_offset += T.par: %s; NOW = %s" % (lmost, T.par_offset, lmost.root_offset),
                             indent=depth)
                else:
                    lmost = LL

                    # protecting from incrementing root offset twice for
                    # leaf nodes (where rmost and lmost are the same node)
                    if lmost is not rmost:
                        lmost.root_offset -= T.par_offset
                        self.log("debug", "%s.root_offset -= T.par: %s; NOW = %s" % (lmost, T.par_offset, lmost.root_offset),
                                 indent=depth)

                self.log("debug", "lmost = %s" % lmost, indent=depth)

                # if LR and RR:
                if T.right is None or ((LR and RR) and LR.depth > RR.depth):
                    rmost = LR
                    rmost.root_offset -= T.par_offset
                    self.log("debug", "%s.root_offset -= T.par: %s; NOW = %s" % (rmost, T.par_offset, rmost.root_offset),
                             indent=depth)
                else:
                    rmost = RR

                    # protecting from incrementing root offset twice for
                    # leaf nodes (where rmost and lmost are the same node)
                    if lmost is not rmost:
                        rmost.root_offset += T.par_offset
                        self.log("debug", "%s.root_offset += T.par: %s; NOW = %s" % (rmost, T.par_offset, rmost.root_offset),
                                 indent=depth)
                self.log("debug", "rmost = %s" % rmost, indent=depth)


                self.log("debug", "PRE-THREADING: LL = %s, RR = %s, T.par_offset = %s" % (LL, RR, T.par_offset)
                         , indent=depth)
                self.log("debug", "PRE-THREADING: L = %s, R = %s, LOFFSUM = %s, ROFFSUM = %s" % (L, R, LOFFSUM, ROFFSUM),
                         indent=depth)
                # if subtrees of T have different heights,
                # check if threading necessary - at most 1 thread
                # will be inserted
                if L and L is not T.left:
                    # create a thread
                    RR.has_thread = True
                    RR.par_offset = abs((RR.root_offset + T.par_offset) - LOFFSUM)
                    self.log("debug", "RR.par_offset =  abs((RR.root_offset: %s + T.par_offset) - LOFFSUM)"
                             % RR.root_offset
                             ,indent=depth)
                    self.log("debug", "SETTING %s.par_offset = %s" % (RR, RR.par_offset),
                             indent=depth)
                    self.log("debug", "THREADING (L) %s to %s" % (RR, L), indent=depth)
                    if LOFFSUM - T.par_offset <= RR.root_offset:
                        RR.left = L
                    else:
                        RR.right = L

                elif R and R is not T.right:
                    # create a thread
                    LL.has_thread = True
                    LL.par_offset = abs((LL.root_offset - T.par_offset) - ROFFSUM)
                    self.log("debug", "LL.par_offset = abs((LL.root_offset: %s - T.par_offset) - ROFFSUM)"
                             % LL.root_offset
                             , indent=depth)
                    self.log("debug", "SETTING %s.par_offset = %s" % (LL, LL.par_offset),
                             indent=depth)

                    self.log("debug", "THREADING (R) %s to %s" % (LL, R), indent=depth)
                    if ROFFSUM + T.par_offset >= LL.root_offset:
                        LL.right = R
                    else:
                        LL.left = R
                self.log("debug", "DONE THREADING", indent=depth)

    def petrify_tr(self):
        """Wrapper function for petrify method in
            Reingold-Tilford algorithm -- assigns
            absolute coordinates after setup_tr has
            determined relative placements"""
        self._petrify_tr(self.root, 0)


    def _petrify_tr(self, T, x):
        """Determines absolute coordinates in
            preorder traversal of the tree and
            removes all 'threads' created from setup"""

        if T:
            self.log("debug", "IN PETRIFY: T = %s, offset = %s" % (T, T.par_offset))
            T.x = x
            if T.has_thread:
                T.has_thread = False
                T.right = None
                T.left = None
            self._petrify_tr(T.left, x - T.par_offset)
            self._petrify_tr(T.right, x + T.par_offset)


    def setup_ws(self):
        """
        Wrapper function to initialize next_xs
        and offset dictionaries and call
        recursive function
        """
        self.next_xs = defaultdict(int)
        self.offsets = defaultdict(int)

        self._setup_ws(self.root, 0)

    def _setup_ws(self, cur_node, depth):
        # assign coordinates in bottom up fashion (postorder)
        for node in cur_node.children():
            self._setup_ws(node, depth+1)

        cur_node.y = depth

        if cur_node.is_leaf():
            # if node is a leaf, simply assign
            # it the next available x coord
            place = self.next_xs[depth]
            cur_node.x = place
        elif len(cur_node.children()) == 1:
            # if one child, place just left of child
            child = cur_node.children()[0]
            if child.val <= cur_node.val:
                place = child.x + 1
            else:
                place = child.x - 1
        else:
            # if two children, center over children
            xsum = cur_node.left.x + cur_node.right.x
            place = xsum / 2

        # determine offset
        self.offsets[depth] = max(self.offsets[depth], self.next_xs[depth] - place)

        if not cur_node.is_leaf():
            cur_node.x = place + self.offsets[depth]

        self.next_xs[depth] += 2
        cur_node.shift = self.offsets[depth]

    def add_shifts(self, cur_node, modsum=0):
        """
        Recursively add x shifts in an
        inorder traversal to place nodes
        in final position
        """
        cur_node.x = cur_node.x + modsum
        modsum += cur_node.shift

        for node in cur_node.children():
            self.add_shifts(node, modsum)


    def render(self):
        # # Reingold-Tilford algorithm
        self.setup_tr()
        self.petrify_tr()

        # determine max/min x/y
        for node in self.root:
            self.max_x = max(node.x, self.max_x)
            self.max_y = max(node.y, self.max_y)
            self.min_x = min(node.x, self.min_x)
            self.min_y = min(node.y, self.min_y)

        # temporary fix to place everything on screen
        for node in self.root:
            node.x += abs(self.min_x)

        # print("x: %i, %i; y: %i, %i" % (self.min_x, self.max_x, self.min_y, self.max_y))


    def render_ws(self):
        """
        Wrapper function to initialize
        'nexts' list and call recursive
        function (Wetherell-Shannon algorithm)
        """
        # NAIVE WS ALGORITHM
        self.next_xs = [0] * (self.max_depth +1 + 1)
        self.max_x = 0
        self.max_y = 0
        self._render_ws(self.root, 0)


        ## improved WS algorithm
        # self.setup_ws()
        # self.add_shifts(self.root)


    def _render_ws(self, cur_node, depth):
        """Naive WS algorithm - doesn't center children"""
        x = self.next_xs[depth]
        y = depth

        cur_node.x = x
        cur_node.y = y

        self.max_x = max(x, self.max_x)

        self.max_y = max(y, self.max_y)

        self.next_xs[depth] += 1
        for node in cur_node.children():
            self._render_ws(node, depth+1)

