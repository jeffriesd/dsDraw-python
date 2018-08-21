from collections import defaultdict
from util import logging_util as log
import logging
from command.command_factory import BSTCommandFactory, BinaryHeapCommandFactory
from drawtools.render import RenderTree
import random
from copy import copy
from datastructures.basic import DataStructure

class TreeNode(object):
    def __init__(self, val, parent=None):
        """
        TreeNode class
        :param val: value stored in node -- currently only using ints
        :param parent: reference to parent node

        left: reference to left child
        right: reference to right child
        xleft: extreme left descendant (leftmost node in bottom layer of subtree)
        xright: extreme right descendant
        par_offset: horizontal offset from this node to parent
        root_offset: horizontal offset from this node to root
        """
        self.val = val
        self.parent = parent
        self.left = None
        self.right = None

        # a subtree consisting of a single node
        # is its own extreme descendant
        self.xleft = self
        self.xright = self

        self.size = 1

        self.depth = -1
        self.x = -1
        self.y = -1

        self.shift = 0

        # used for Reingold-Tilford algorithm
        self.par_offset = 0
        self.root_offset = 0
        self.has_thread = False

        self.color = "white"

    def __repr__(self):
        return "Node(%s)" % self.val

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
        """Returns list of _children if any exist"""
        return [n for n in [self.left_child(), self.right_child()] if n is not None]

    def left_child(self):
        return self.left

    def right_child(self):
        return self.right

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node

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

    def get_xleft(self):
        return self.xleft

    def get_xright(self):
        return self.xright

    def update_extremes(self):
        """
        Update extreme descendants picking from
        only immediate _children. Only 4 possible choices.
        """
        if self.is_leaf():
            self.xleft = self
            self.xright = self
            return

        child_extremes = [x for c in self.children()
                          for x in c.get_extremes()]

        # get max depth
        max_d = max([x.depth for x in child_extremes])

        deepest = list(filter(lambda n: n.depth == max_d, child_extremes))

        # self.xleft = min(deepest, key=lambda n: n.val)
        # self.xright = max(deepest, key=lambda n: n.val)
        self.xleft = deepest[0]
        self.xright = deepest[-1]

    def update_child_depths(self, depth=0):
        """"Recursively update depths in O(n) traversal of subtree"""
        self._update_child_depths(self, depth)

    def _update_child_depths(self, cur_node, depth):
        if cur_node is None:
            return
        cur_node.depth = depth
        self._update_child_depths(cur_node.left_child(), depth+1)
        self._update_child_depths(cur_node.right_child(), depth+1)

    def update_descendants_bottom_up(self):
        self._update_descendants_bottom_up(self)

    def _update_descendants_bottom_up(self, cur_node):

        if cur_node is None:
            return

        self._update_descendants_bottom_up(cur_node.left_child())
        self._update_descendants_bottom_up(cur_node.right_child())

        cur_node.update_extremes()

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
        return None

    def is_left_child(self):
        return self is self.parent.left


class Tree(DataStructure):
    def __init__(self, root=None, name=None):
        self.root = root
        self.max_depth = 0

        # assign name for getting corresponding render object
        self.name = name

    def __repr__(self):
        return "Tree structure with root %s" % self.root

    def __iter__(self):
        return iter(self.root)

    def set_name(self, name):
        self.name = name

    def preorder(self):
        """Wrapper for TreeNode preorder"""
        return self.root.preorder()

    def postorder(self):
        """Wrapper for TreeNode postorder"""
        return self.root.postorder()



    def get_render_class(self):
        """
        Returns appropriate render class for BST
        """
        return RenderTree


class BST(Tree):
    """
    Binary search tree class. Keeps track of
    height of tree (max_depth) and maintains a reference
    to root TreeNode
    """
    def __init__(self, prebuild_size=0, root=None, name=None):
        super().__init__(root, name)

        if prebuild_size:
            prebuild_size = int(prebuild_size)
            numbers = list(range(prebuild_size))
            random.shuffle(numbers)
            for n in numbers:
                self.insert(n)

    def __repr__(self):
        return "BST with root %s" % self.root

    def get_command_factory(self):
        """
        Return appropriate command factory for BST,
        initialized with reference to 'receiver'
        """
        return BSTCommandFactory(self)

    def insert(self, el, change_color=False):
        """
        Wrapper method to call recursive insert.
        :param el: element being inserted
        :param change_color: shows traversal of tree for visual purposes
        """
        self.log("info", "calling wrapper insert func with root %s to insert %i" % (self.root, el))
        if self.root:
            self.root = self._insert(self.root, el, change_color)
        else:
            self.root = TreeNode(el)

    def _insert(self, cur_node, el, change_color):
        """
        Recursive insert function
        :param cur_node: current working node
        :param el: value being inserted
        :param depth: current depth in tree
        :param change_color: shows traversal of tree for visual purposes
        """

        self.log("debug", "inserting %i; current node is %s" % (el, cur_node))

        # change color to show traversal of tree
        if change_color:
            cur_node.color = 'red'
            self.control.my_renders[self.name].display(do_render=False, do_sleep=True)
            cur_node.color = 'white'

        if el <= cur_node.val:
            self.log("debug", "%i <= %i; going left" % (el, cur_node.val))
            if cur_node.left:
                cur_node.left = self._insert(cur_node.left, el, change_color)
            else:
                self.log("debug", "new leaf (%s)" % (el))
                cur_node.left = TreeNode(el, parent=cur_node)
        else:
            self.log("debug", "%i > %i; going right" % (el, cur_node.val))
            if cur_node.right:
                cur_node.right = self._insert(cur_node.right, el, change_color)
            else:
                self.log("debug", "new leaf (%s)" % (el))
                cur_node.right = TreeNode(el, parent=cur_node)

        # update size
        cur_node.inc_size()

        return cur_node

    def remove(self, el, change_color=False):
        """Wrapper method for recursive remove method"""
        self.log("info", "calling wrapper remove func with root %s to remove %i" % (self.root, el))

        if self.find(el, change_color=False):
            # if tree has exactly one node
            if self.root.size == 1:
                self.root = None
            else:
                self.root = self._remove(self.root, el, change_color)

        else:
            raise Exception("Can't remove %s. Not present in tree" % el)

    def _remove(self, cur_node, el, change_color):
        """Recursive remove method. Three possible cases:
            1. cur_node is leaf, simply remove it
            2. cur_node has one child, "short circuit" method
            3. cur_node has two _children. Find predecessor of cur_node,
               swap with cur_node and then delete cur_node from its new position"""

        if cur_node is None:
            return cur_node

        # change color of current node to show traversal of tree
        if change_color:
            cur_node.color = 'red'
            self.control.my_renders[self.name].display(do_render=False, do_sleep=True)
            cur_node.color = 'white'

        if el == cur_node.val:
            if cur_node.left is None:
                return cur_node.right
            elif cur_node.right is None:
                return cur_node.left
            else:
                # swap current node with predecessor and
                # then remove it from its new location
                pred = cur_node.predecessor()
                cur_node.val = pred.val
                cur_node.left = self._remove(cur_node.left, pred.val, change_color)

        # recurse left or right
        elif el < cur_node.val:
            cur_node.left = self._remove(cur_node.left, el, change_color)
        elif el > cur_node.val:
            cur_node.right = self._remove(cur_node.right, el, change_color)

        cur_node.update_size()

        return cur_node

    def _remove_swap(self, cur_node, el, change_color):
        """Recursive remove method. Three possible cases:
            1. cur_node is leaf, simply remove it
            2. cur_node has one child, simply swap and remove
            3. cur_node has two _children. Find successor of cur_node,
               swap with cur_node and then delete cur_node from its new position"""
        if cur_node is None:
            return

        # change color of current node to show traversal of tree
        if change_color:
            cur_node.color = 'red'
            self.control.my_renders[self.name].display(do_render=False, do_sleep=True)
            cur_node.color = 'white'

        if el == cur_node.val:
            # case 1
            if cur_node.is_leaf():
                return None
            # case 2
            elif cur_node.size == 2:
                # swap with child (only need to swap values)
                child = cur_node.children()[0]
                cur_node = self._remove_swap(cur_node, child.val, change_color)
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
                        ps.parent.left = self._remove_swap(ps, ps.val, change_color)
                    else:
                        ps.parent.right = self._remove_swap(ps, ps.val, change_color)

                    # when final swap happens, make O(log n) traversal
                    # back up to root to update sizes and descendants
                    if ps.is_leaf():
                        node = ps.parent
                        while node:
                            node.dec_size()
                            node.update_extremes()
                            node = node.parent

        # recurse left or right
        elif el < cur_node.val:
            cur_node.left = self._remove_swap(cur_node.left, el, change_color)
        elif el > cur_node.val:
            cur_node.right = self._remove_swap(cur_node.right, el, change_color)

        cur_node.update_size()
        cur_node.update_extremes()

        return cur_node

    def find(self, el, change_color):
        """Wrapper method for recursive find function"""
        return self._find(self.root, el, change_color)

    def _find(self, cur_node, el, change_color):
        """Standard recursive find method O(logn)"""
        # if cur_node is None:
        #     return None

        # change color of current node to show traversal of tree
        if change_color:
            cur_node.color = "red"
            self.control.my_renders[self.name].display(do_render=False, do_sleep=True)
            cur_node.color = "white"

        if cur_node.val == el:
            return cur_node

        if cur_node.is_leaf():
            return None

        if el <= cur_node.val:
            return self._find(cur_node.left, el, change_color)
        else:
            return self._find(cur_node.right, el, change_color)

    def rotate_left(self, node_a, node_b):
        """
        Perform left rotation with node_a and node_b.

        precondition: node_b is right child of node_a
        postcondition: node_a is left child of node_b

            A                       B
          /  \                     / \
         t1   B     becomes       A  t3
             / \                 / \
            t2  t3              t1  t2

        which subtrees may change?
            - node_a
            - node_b
            - parent of node_a

        Had to add O(n) traversal of subtrees to update
        depths and O(log(n)) walk to root to update sizes
        and extreme descendants
        """
        # precondition
        if node_b is not node_a.right:
            msg = "Cannot do left rotation: %s is not right child of %s" % (node_b, node_a)
            raise ValueError(msg)

        # attach t_2 to a, its depth doesnt change
        t_2 = node_b.left
        node_a.right = t_2
        if t_2:
            t_2.parent = node_a
        node_b.left = None

        # attach node_a as left child of node_b
        node_b.left = node_a

        # special case if node_a is root
        if node_a is self.root:
            self.root = node_b
        else:
            # make link from parent to node_b
            if node_a.is_left_child():
                node_a.parent.left = node_b
            else:
                node_a.parent.right = node_b

        # update parent references
        node_b.parent = node_a.parent
        node_a.parent = node_b

        # also need to update sizes for any ancestors
        node = node_a
        while node:
            node.update_size()
        #     node.update_extremes()
            node = node.parent

    def rotate_right(self, node_a, node_b):
        """
        Perform right rotation with node_a and node_b

        precondition: node_b is left child of node_a
        postcondition: node_a is right child of node_b

        Includes final O(log(n)) traversal to update depths
        and extreme descendant info.
        """

        if node_b is not node_a.left:
            msg = "Cannot do right rotation: %s is not left child of %s" % (node_b, node_a)
            raise ValueError(msg)

        # subtree between b and a becomes new left
        # child of node_a
        t_2 = node_b.right
        node_a.left = t_2
        if t_2:
            t_2.parent = node_a

        # attach node_a as right child of node_b
        node_b.right = node_a

        # special case if node_a is root
        if node_a is self.root:
            self.root = node_b
        else:
            # make connections from a's parent to b
            if node_a.is_left_child():
                node_a.parent.left = node_b
            else:
                node_a.parent.right = node_b

        # update parent references
        node_b.parent = node_a.parent
        node_a.parent = node_b

        # walk up to root and update sizes and extreme descendants
        node = node_a
        while node:
            node.update_size()
            node = node.parent


class HeapNode(TreeNode):
    def __init__(self, val, heap, index=-1, parent=None):
        """
        Heap node must be initialized with reference
        to the heap class for getting left and right
        _children as well as parent references."""
        super().__init__(val, parent=parent)

        self.heap = heap

    def left_child(self):
        """Return left child of heap using index"""
        index = self.heap.heap_array.index(self)
        return self.heap.heap_left(index)

    def right_child(self):
        index = self.heap.heap_array.index(self)
        return self.heap.heap_right(index)

    def is_leaf(self):
        return len(self.children()) == 0


class BinaryHeap(Tree):

    def __init__(self, prebuild_size=0, root=None, name=None):
        self.heap_array = []
        super().__init__(root, name)

        self.root = root
        self.max_depth = 0

        # assign name for getting corresponding render object
        self.name = name

        if prebuild_size:
            prebuild_size = int(prebuild_size)
            numbers = list(range(prebuild_size))
            random.shuffle(numbers)
            for n in numbers[:prebuild_size//2]:
                self.insert_key(n)
    @property
    def root(self):
        try:
            return self.heap_array[0]
        except IndexError:
            return None

    @root.setter
    def root(self, node):
        try:
            self.heap_array[0] = node
        except IndexError:
            self.heap_array.append(node)

    def __repr__(self):
        return "Binary heap with root %s" % self.root

    def print_heap(self):
        print(list(map(lambda node: node.val, self.heap_array)))

    def get_command_factory(self):
        return BinaryHeapCommandFactory(self)

    def find(self, key, change_color=False):
        """O(n) traversal"""
        for node in self.heap_array:
            if change_color:
                node.color = 'red'
                self.control.my_renders[self.name].display(do_render=True, do_sleep=True)
                node.color = 'white'
            if node.val == key:
                return node
        return None

    def parent_index(self, index):
        return (index - 1) // 2 if index > 0 else 0

    def left_index(self, index):
        return 2 * index + 1

    def right_index(self, index):
        return 2 * index + 2

    def heap_parent(self, index):
        try:
            return self.heap_array[(index - 1) // 2]
        except IndexError:
            return None

    def heap_left(self, index):
        try:
            return self.heap_array[index * 2 + 1]
        except IndexError:
            return None

    def heap_right(self, index):
        try:
            return self.heap_array[index * 2 + 2]
        except IndexError:
            return None

    def insert_key(self, key, change_color=False):
        """
        Insert new node at the end of the array
        and sift up until heap property satisfied
        Runtime: O(logn)
        """

        if self.root is None:
            self.root = HeapNode(key, self)
            return

        new_index = len(self.heap_array)
        new_node = HeapNode(key, self, parent=self.heap_array[self.parent_index(new_index)])

        self.heap_array.append(new_node)
        self.sift_up(new_index, change_color)

    def decrease_key(self, node, new_value, change_color=False):
        """
        Decrease key value and sift up/down as needed.
        """
        node.val = new_value
        index = self.heap_array.index(node)
        p = self.heap_parent(index)
        l = self.heap_left(index)
        r = self.heap_right(index)

        # check heap property
        if node.val < p.val:
            self.sift_up(index, change_color=change_color)
        elif l.val < node.val or r.val < node.val:
            self.sift_down(index, change_color=change_color)

    def remove_min(self, change_color=False):
        """
        Remove and return minimum element (root)
        of the heap by swapping it with the final element
        in the array and sifting that element down
        """
        # save node so it can be returned at end
        min = copy(self.root)

        if len(self.heap_array) == 1:
            self.heap_array = []
            return min

        # swap min with final node,
        # remove last element and sift down
        last = self.heap_array[-1]
        self.root = last
        self.heap_array = self.heap_array[:-1]

        self.sift_down(0, change_color=change_color)

        return min

    def sift_down(self, index, change_color):
        """
        Swap with child nodes until heap
        property satisfied.
        Runtime: O(logn)
        """
        p = self.heap_array[index]
        l = self.heap_left(index)
        r = self.heap_right(index)
        if not r or l < r:
            child = l
            index = self.left_index(index)
        else:
            child = r
            index = self.right_index(index)

        while p.val > child.val:
            if change_color:
                child.color = 'red'
                self.control.my_renders[self.name].display(do_render=True, do_sleep=True)
                child.color = 'white'

            # swap nodes
            temp = p.val
            self.heap_array[self.parent_index(index)].val = child.val
            self.heap_array[index].val = temp

            # move index down heap and
            # update pointers
            l = self.heap_left(index)
            r = self.heap_right(index)
            if not r or l < r:
                index = self.left_index(index)
            else:
                index = self.right_index(index)

            # stop index from going off end of list
            if child.is_leaf():
                break
            child = self.heap_array[index]
            # p = self.heap_array[self.parent_index(index)]
            p = self.heap_parent(index)

    def sift_up(self, index, change_color):
        """
        Swap with parent nodes until heap
        property satisfied.
        Runtime: O(logn)
        """
        child = self.heap_array[index]
        p_index = self.parent_index(index)
        p = self.heap_array[p_index]

        while p.val > child.val:
            if change_color:
                child.color = 'red'
                self.control.my_renders[self.name].display(do_render=True, do_sleep=True)
                child.color = 'white'

            # swap nodes
            temp = p
            self.heap_array[self.parent_index(index)] = child
            self.heap_array[index] = temp

            # move index up heap and
            # update pointers
            index = self.parent_index(index)
            child = self.heap_array[index]
            p = self.heap_array[self.parent_index(index)]

if __name__ == '__main__':
    my_nodes = [21, 25, 17, 9, 7, 19]
                # 8, 20, 10, 11, 28, 26, 24, 5, 23]

    h = BinaryHeap()
    for n in my_nodes:
        h.insert_key(n)
    h.print_heap()

    print(h.parent_index(0))