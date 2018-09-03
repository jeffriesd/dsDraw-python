from datastructures.basic import DataStructure
import random


class ArrayNode(object):
    def __init__(self, value, color=None):
        self.value = value
        self.color = color or "white"

    def __repr__(self):
        return "ArrayNode(%s)" % self.value


class Array(DataStructure):
    def __init__(self, prebuild_values=None, size=0, hide=False):
        """
        Basic Array class composed of
        ArrayNodes. ArrayNodes currently contain
        information about value and color.

        :param prebuild_values: some iterable of _array
        """
        super().__init__()

        if prebuild_values:
            self._array = [ArrayNode(value=x) for x in prebuild_values]
            self.size = len(self._array)
        elif size:
            self.size = size
            self._array = [ArrayNode(value=random.randint(0, self.size * 10)) for _ in range(self.size)]
        else:
            # 8 cells fit nicely on screen as default length
            self.size = 8
            self._array = [ArrayNode(value=random.randint(0, self.size * 10)) for _ in range(self.size)]

        self.hide_values = hide

    def __repr__(self):
        return "Array of size %s" % self.size

    def __iter__(self):
        return self._array

    def __getitem__(self, index):
        """
        Access _array.
        """
        return self._array[index].value

    def __setitem__(self, index, value):
        """
        Modify array value at index. Keep color
        of node currently at index.
        """
        cur_color = self._array[index].color
        self._array[index] = ArrayNode(value, color=cur_color)

    def clone(self):
        clone = Array(prebuild_values=self._array)
        return clone

    def get_render_class(self):
        return None

if __name__ == '__main__':
    a = Array(size=10)
    print(a._array)
    a[0] = 999
    print(a._array)