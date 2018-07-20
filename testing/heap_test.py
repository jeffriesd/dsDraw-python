import unittest
import random
from datastructures import tree
from drawtools.render import RenderTree


class GenericHeapTest(unittest.TestCase):
    """
    Generic heap tests for stored
    values of depth and size, heap property.
    Builds heap using only inserts.
    """

    def setUp(self):
        """Build a BST of size 50 using only inserts"""
        self.heap = tree.BinaryHeap()
        self.size = 500

        self.original_values = random.sample(list(range(self.size * 2)), self.size)

        for n in self.original_values:
            self.heap.insert_key(n)

        # render to update depths and extreme descendants
        render_obj = RenderTree(self.heap, None)
        render_obj.render()

    def test_heap_property(self):

        for node in self.heap:
            for c in node.children():
                self.assertLess(node, c)

    def test_duplicate_coordinates(self):
        """
        Check if the tree has any duplicate coordinates
        after creating render object to perform Reingold-Tilford algorithm
        """

        all_xy = [(node.x, node.y) for node in self.heap.root]

        for node in self.heap:
            coordinate = (node.x, node.y)
            # check that each coordinate only occurs once
            occurrences = all_xy.count(coordinate)

            message = "%i occurrences of %s. Duplicate coordinates" % (occurrences, coordinate)

            self.assertEqual(occurrences, 1, msg=message)

