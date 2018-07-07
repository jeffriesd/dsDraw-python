import unittest
from util import build_tree
import random
from datastructures import tree


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

        numbers = random.sample(list(range(self.size * 2)), self.size)

        for n in numbers:
            self.tree.insert(n)

    def test_sizes(self):
        """Check sizes of each subtree (inorder traversal)"""
        for node in self.tree.root:
            size = 0

            # TreeNode class iterator produces inorder traversal
            for subchild in node:
                size += 1
            self.assertEqual(node.get_size(), size)

    def test_depths(self):
        """Check depth of each subtree by
            making node-to-root traversal for each subtree.
            Root node has depth 0"""

        for node in self.tree.root:
            depth = 0

            cursor = node
            while cursor is not self.tree.root:
                cursor = cursor.parent
                depth += 1

            # check this depth against stored depth value
            self.assertEqual(depth, node.depth)

    def test_bst_property(self):
        """Check binary search tree property satistfying
            left <= parent < right"""

        for node in self.tree.root:
            # left <= parent
            if node.left_child():
                self.assertLessEqual(node.left_child().val, node.val)
            if node.right_child():
                self.assertLess(node.val, node.right_child().val)

    def test_extreme_descendants(self):
        pass

    def test_duplicate_coordinates(self):
        """
        Check if the tree has any duplicate coordinates
        after calling render (Reingold-Tilford algorithm)
        """

        self.tree.render()

        all_xy = [(node.x, node.y) for node in self.tree.root]
        all_1 = all([all_xy.count((node.x, node.y)) == 1 for node in self.tree.root])

        for node in self.tree.root:
            coordinate = (node.x, node.y)
            # check that each coordinate only occurs once
            occurrences = all_xy.count(coordinate)

            message = "%i occurrences of %s. Duplicate coordinates" % (occurrences, coordinate)

            self.assertEqual(occurrences, 1, msg=message)


class GenericBSTRemoveTest(unittest.TestCase):

    def setUp(self):
        """Build a BST of size 50 using only inserts"""
        self.tree = tree.BST()
        self.size = 500

        numbers = random.sample(list(range(self.size * 2)), self.size)

        for n in numbers:
            self.tree.insert(n)

        to_remove = random.sample(numbers, self.size // 2)

        for n in to_remove:
            self.tree.remove(n)




if __name__ == '__main__':
    unittest.main()
