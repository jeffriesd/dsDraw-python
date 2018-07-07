from datastructures import tree
import random


def build_tree(n, max_val, t=None):
    """Builds a tree of unique integer elements"""
    t = tree.BST() if t is None else t
    max_val = max(max_val, n)
    r_set = random.sample(range(max_val), n)
    for x in r_set:
        t.insert(x)
    return t