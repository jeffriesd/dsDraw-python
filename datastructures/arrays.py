from datastructures.basic import DataStructure
from drawtools.render import RenderArray
from drawtools import dsDraw_colors
from datastructures.basic import InteractiveDataStructure
from datastructures.interactive import InteractiveArray
from util.exceptions import InvalidCommandError
import time
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

    def clone(self):
        clone = Array(prebuild=self._array)
        return clone

    def get_render_class(self):
        return RenderArray

    def get_interactive_class(self):
        return InteractiveArray


