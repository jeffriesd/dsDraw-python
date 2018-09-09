import unittest
import random
from datastructures import tree
from drawtools.render import RenderTree


class GenericBSTTest(unittest.TestCase):
    """
    Generic (not balanced) BST tests for stored
    values of depth and size, bst property.
    Builds tree using only inserts.
    """

    def setUp(self):
        """Build a BST of size 50 using only inserts"""
        self.tree = tree.BST()
        self.size = 500

        self.original_values = random.sample(list(range(self.size * 2)), self.size)

        for n in self.original_values:
            self.tree.insert(n)

        # render to update depths and extreme descendants
        render_obj = RenderTree(self.tree, None)
        render_obj.render()

    def test_sizes(self):
        """Check sizes of each subtree (inorder traversal)"""
        for node in self.tree.root:
            size = 0

            # iterate through subtree (including root node)
            for _ in node:
                size += 1
            self.assertEqual(node.get_size(), size)

    def test_depths(self):
        """Check depth of each subtree by
            making node-to-root traversal for each subtree.
            Root node has depth 0"""

        self._test_depths(self.tree.root, 0)

    def _test_depths(self, cur_node, depth):
        if not cur_node:
            return
        self._test_depths(cur_node.left, depth+1)
        self.assertEqual(cur_node.depth, depth)
        self._test_depths(cur_node.right, depth+1)


    def test_bst_property(self):
        """Check binary search tree property satistfying
            left <= parent < right"""

        for node in self.tree:
            # left <= parent
            if node.left_child():
                self.assertLessEqual(node.left_child().value, node.value)
            if node.right_child():
                self.assertLess(node.value, node.right_child().value)

    def test_extreme_descendants(self):
        """
        Test if extreme descendants are correct for all subtrees.
        Extreme descendants are min/max values of those
        at deepest level of subtree.
        """

        for subtree in self.tree:
            if subtree.is_leaf():
                xleft = xright = subtree
            else:
                all_descendants = list(subtree)
                max_d = max([node.depth for node in all_descendants])
                only_max_depth = list(filter(lambda n: n.depth == max_d, all_descendants))
                xleft = min(only_max_depth, key=lambda n: n.value)
                xright = max(only_max_depth, key=lambda n: n.value)

            self.assertEqual(xleft, subtree.xleft, msg="Extreme left of %s should be %s" % (subtree, xleft))
            self.assertEqual(xright, subtree.xright, msg="Extreme right of %s should be %s" % (subtree, xright))


    def test_duplicate_coordinates(self):
        """
        Check if the tree has any duplicate coordinates
        after creating render object to perform Reingold-Tilford algorithm
        """

        all_xy = [(node.x, node.y) for node in self.tree.root]

        for node in self.tree:
            coordinate = (node.x, node.y)
            # check that each coordinate only occurs once
            occurrences = all_xy.count(coordinate)

            message = "%i occurrences of %s. Duplicate coordinates" % (occurrences, coordinate)

            self.assertEqual(occurrences, 1, msg=message)


class GenericBSTRemoveTest(GenericBSTTest):

    def setUp(self):
        """Build a BST of size self.size and then remove half of them."""
        super().setUp()

        to_remove = random.sample(self.original_values, self.size // 2)

        for n in to_remove:
            self.tree.remove(n)

        # render to update depths and extreme descendants
        render_obj = RenderTree(self.tree, None)
        render_obj.render()


class GenericBSTRotateTest(GenericBSTTest):

    def setUp(self):
        """Build a BST and then randomly rotate some nodes"""
        super().setUp()

        r = self.tree.root
        rr = r .right

        self.tree.rotate_left(r, rr)

        nodes = list(self.tree)

        for n in random.sample(nodes, self.size // 2):
            r = n.right_child()
            l = n.left_child()
            if r:
                self.tree.rotate_left(n, r)
            r = n.right_child()
            l = n.left_child()
            if not r and l:
                self.tree.rotate_right(n, l)

        # render to update depths and extreme descendants
        render_obj = RenderTree(self.tree, None)
        render_obj.render()

if __name__ == '__main__':
    unittest.main()

