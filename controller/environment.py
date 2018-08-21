from util.exceptions import InvalidCommandError

class VariableEnvironment(object):

    def __init__(self, control):
        """
        Handles variables created by
        user in console.

        :param control: reference to control object
        """
        self.control = control
        self.variables = {}


    def __getitem__(self, var_name):
        """
        Do any parsing for instances
        of graph:nodes or other references
        """
        if ":" in var_name:
            return self.get_attribute(var_name)

        return self.variables[var_name]

    def __setitem__(self, var_name, value):
        self.variables[var_name] = value

    def __delitem__(self, var_name):
        del self.variables[var_name]

    def get_attribute(self, attribute_string):
        """
        Gets attribute/property from a variable stored in
        control.my_variables.

        :param attribute_string: e.g. "graph2:nodes"

                other examples:

                bst_a:root:left:val
        """

        var_names = attribute_string.split(":")

        attr = None

        while var_names:

            # get first two names
            object_name, attr_name = var_names[:2]

            # if still reading strings and not using
            # object references
            if type(object_name) is str:
                try:
                    object = self.variables[object_name]
                except KeyError:
                    raise InvalidCommandError("Cannot resolve '%s': no model named '%s'" % (attribute_string, object_name))
            else:
                # otherwise the list element may be the node
                # and not the name of the node
                object = object_name

            try:
                attr = object.__getattribute__(attr_name)
            except AttributeError:
                raise InvalidCommandError(
                    "Cannot resolve '%s': no attribute '%s' for model '%s'" % (attribute_string, attr_name, object_name))

            if len(var_names) > 2:
                var_names =  [attr] + var_names[2:]
            else:
                var_names = []

        return attr



