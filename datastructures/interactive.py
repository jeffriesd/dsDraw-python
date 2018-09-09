import time
from datastructures.basic import InteractiveDataStructure
from datastructures import tree
from drawtools import dsDraw_colors
from util.exceptions import InvalidCommandError


class InteractiveArray(InteractiveDataStructure):
    def __init__(self, control, model, render):
        InteractiveDataStructure.__init__(self, control, model, render)
        self._hide_values = False
        self._hide_indices = False

    def __getitem__(self, index):
        """
        Access array
        """
        return self._model._array[index].value

    def __setitem__(self, index, value):
        """
        Modify array
        """
        self.add_state_to_history()
        self._model._array[index].value = value
        self._render.display()

    def color(self, color_name, *indices):
        """
        Assign a new color to array[index].
        Must be valid color (in dsDraw_colors)
        :param indices: index or tuple of indices
        :param color_name: key to dsDraw_colors dict

        If no indices provided, color entire array.
        If one index provided, color array[index]
        If two provided, color i to j, inclusive
        """

        try:
            color = dsDraw_colors[color_name]
        except KeyError:
            raise Exception("Invalid color '%s'" % color_name)

        self.add_state_to_history()

        # if no indices provided, color entire array
        if len(indices) == 0:
            low, high = 0, self._model.size
        elif len(indices) == 1:
            low, high = indices[0], indices[0] + 1
        else:
            low, high = indices
            high += 1

        for i in range(low, high):
            self._model._array[i].color = color

        self._render.display()

    def swap(self, i, j):
        """
        Perform a swap of elements i and j
        with animation.

        Animation: squares rise above array (.5s)
                   squares move horizontally to change positions (1s)
                   squares lower into new positions (.5s)
        """
        if i == j:
            raise InvalidCommandError("Cannot swap element %s with itself" % i)
        if i < 0 or i >= self._model.size:
            raise InvalidCommandError("Index %s out of bounds" % i)
        if j < 0 or j >= self._model.size:
            raise InvalidCommandError("Index %s out of bounds" % j)

        self.add_state_to_history()

        # require i < j
        if j < i:
            temp = i
            i = j
            j = temp

        rect_i = self._model.name + "_" + str(i)
        rect_j = self._model.name + "_" + str(j)

        # raise rectangles to top so they cover indices when
        # moving over them
        self._render.canvas.tag_raise(rect_i)
        self._render.canvas.tag_raise(rect_j)

        # number of steps to move vertically, horizontally
        # (each step takes .1s)
        v_steps = 5
        h_steps = 10

        tick = 0.075

        # translate rectangles up by 2 * cell_h
        y_translate = 2 * self._render.cell_h
        y_step = y_translate / v_steps

        x_i, _, _, _ = self._render.canvas.coords(rect_i)
        x_j, _, _, _ = self._render.canvas.coords(rect_j)
        x_translate = int(x_j - x_i)
        x_step = x_translate / h_steps

        # do vertical translation upwards
        for _ in range(v_steps):
            self._render.canvas.move(rect_i, 0, -y_step)
            self._render.canvas.move(rect_j, 0, -y_step)
            time.sleep(tick)

        # brief pause
        time.sleep(tick)

        # horizontal translation
        for _ in range(h_steps):
            self._render.canvas.move(rect_i, x_step, 0)
            self._render.canvas.move(rect_j, -x_step, 0)
            time.sleep(tick)

        time.sleep(tick)

        # put rectangles back in place
        for _ in range(v_steps):
            self._render.canvas.move(rect_i, 0, y_step)
            self._render.canvas.move(rect_j, 0, y_step)
            time.sleep(tick)

        # finally swap the elements in actual data structure
        temp = self._model._array[i]
        self._model._array[i] = self._model._array[j]
        self._model._array[j] = temp

        # redraw array so tags get reassigned
        self._render.display()

    def hide_values(self):
        """
        Toggles hidden values
        """
        self._render._hide_values = not self._render._hide_values
        self._render.display()

    def hide_indices(self):
        """
        Toggles hidden indices
        """
        self._render._hide_indices = not self._render._hide_indices
        self._render.display()

    def compress(self):
        """
        Toggle _force_compress, which
        causes array to compress regardless of size relative to canvas
        """
        self._render._force_compress = not self._render._force_compress
        self._render.display()


class InteractiveBST(InteractiveDataStructure):
    def __init__(self, control, model, render):
        InteractiveDataStructure.__init__(self, control, model, render)

    def root(self):
        return self._model.root

    def insert(self, value):
        """
        Insert new node into BST
        """
        self.add_state_to_history()
        self._model.insert(value)
        self._render.display()

    def remove(self, value):
        """
        Remove node from BST
        """
        self.add_state_to_history()
        self._model.remove(value)
        self._render.display()

    def find(self, value):
        """
        Perform find operation on BST and return
        the value.
        """
        tree_node = self._model.find(value)
        return tree_node

    def rotate(self, node_a, node_b):
        """
        Perform rotation of two nodes.
        Determine if left, right, or neither possible.

        rotate_right(self, node_a, node_b):
            precondition: node_b is left child of node_a

        rotate_left(self, node_a, node_b):
            precondition: node_b is right child of node_a
        """
        self.add_state_to_history()
        if not isinstance(node_a, tree.TreeNode):
            node_a = self._model.find(node_a)
        if not isinstance(node_b, tree.TreeNode):
            node_b = self._model.find(node_b)

        # left rotation
        if node_b is node_a.left:
            self._model.rotate_right(node_a, node_b)
        elif node_a is node_b.left:
            self._model.rotate_right(node_b, node_a)
        elif node_b is node_a.right:
            self._model.rotate_left(node_a, node_b)
        elif node_a is node_b.right:
            self._model.rotate_left(node_b, node_a)
        else:
            raise InvalidCommandError("Cannot rotate unconnected nodes %s, %s" % (node_a.value, node_b.value))

        self._render.display()


class InteractiveBinaryHeap(InteractiveDataStructure):

    def __init__(self, control, model, render):
        InteractiveDataStructure.__init__(self, control, model, render)

    def insert(self, key):
        """
        Insert new key into heap
        """
        self.add_state_to_history()
        self._model.insert_key(key)
        self._render.display()

    def remove_min(self):
        """
        Return min value from heap
        """
        self.add_state_to_history()
        heap_node = self._model.remove_min()
        self._render.display()
        return heap_node.value

    def decrease_key(self, heap_node, new_value):
        """
        Decrease key and sift down or up according to
        heap property violations.
        :param heap_node: reference to HeapNode
        :param new_value: new value of HeapNode
        """
        self.add_state_to_history()
        self._model.decrease_key(heap_node, new_value)
        self._render.display()