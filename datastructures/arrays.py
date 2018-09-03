from datastructures.basic import DataStructure
from drawtools.render import RenderArray
from drawtools import dsDraw_colors
import random


class ArrayNode(object):
    def __init__(self, value, color=None):
        self.value = value
        self.color = color or "white"

    def __repr__(self):
        return "ArrayNode(%s)" % self.value


class Array(DataStructure):
    def __init__(self, prebuild=None, hide=False):
        """
        Basic Array class composed of
        ArrayNodes. ArrayNodes currently contain
        information about value and color.

        :param prebuild: integer or iterable of values
        """
        super().__init__()

        if prebuild is None:
            # 8 cells fit nicely on screen as default size
            self.size = 8
            self._array = [ArrayNode(value=random.randint(0, 99)) for _ in range(self.size)]
        elif isinstance(prebuild, int):
            self.size = prebuild
            self._array = [ArrayNode(value=random.randint(0, 99)) for _ in range(self.size)]
        else:
            # prebuild is some iterable
            self._array = [ArrayNode(value=x) for x in prebuild]
            self.size = len(self._array)

        self.hide_values = hide

    def __repr__(self):
        return "Array of size %s" % self.size

    def __iter__(self):
        for x in self._array:
            yield x

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        """
        Access _array
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
        clone = Array(prebuild=self._array)
        return clone

    def get_render_class(self):
        return RenderArray

    def color(self, indices, color_name):
        """
        Assign a new color to array[index].
        Must be valid color (in dsDraw_colors)
        :param indices: index or tuple of indices
        :param color_name: key to dsDraw_colors dict
        """
        try:
            color = dsDraw_colors[color_name]
        except KeyError:
            raise Exception("Invalid color '%s'" % color_name)

        if isinstance(indices, int):
            index = indices
            self._array[index].color = color
        else:
            low, high = indices
            for i in range(low, high):
                self._array[i].color = color


if __name__ == '__main__':
    a = Array(size=10)
    print(a._array)
    a[0] = 999
    print(a._array)