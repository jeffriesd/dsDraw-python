from datastructures import tree


class ModelFactory(object):
    def __init__(self):
        self.model_types = {
            "bst": tree.BST,
            "heap": tree.BinaryHeap
        }

    def create_model(self, model_type_name, *other_args):
        try:
            model_class = self.model_types[model_type_name]
            return model_class(*other_args)
        except KeyError as e:
            raise e