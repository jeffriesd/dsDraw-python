import logging
import util.logging_util as log
from copy import copy
from collections import deque


class DataStructure(object):

    def set_name(self, name):
        self.name = name

    def set_control(self, control):
        """Sets reference for control object"""
        self.control = control

    def set_logger(self, logger):
        self.logger = logger
        self.clear_log()
        self.log("info", "\n\n\t----- new run -----\n")

        # excluding debug information
        self.log("info", "setting level to info")
        self.logger.setLevel(logging.INFO)

    def clear_log(self):
        with open('../logs/model_log.log', 'w') as _:
            pass

    def log(self, level_str, message, indent=0):
        """
        Wrapper function for logging -- data structure may be created
        before the control object (and thus the logger) has been initialized
        :param level_str: string specifying logging level
        :param message: message to log
        :return:
        """
        message = "\t" * indent * 1 + message

        try:
            if self.logger:
                log_func = log.to_function(self.logger, level_str)
                log_func(message)
        except AttributeError:
            pass
            # print("no logger ; message was %s" % message)



    def clone(self):
        raise NotImplementedError("Clone not implemented for %s" % self)


class InteractiveDataStructure(object):
    """
    Class to bind together render object and
    model so that animated commands can be performed
    on the data structure without the DataStructure
    object needing to call the render object.

    This is the class that is exposed to the user
    and contains the methods they can use to interact
    with the data structure.

    Also maintains state information and allows for
    undo/redo
    """
    def __init__(self, control, model, render):

        self._control = control
        self._model = model
        self._render = render
        self._state_history = deque(maxlen=10)

    def add_state_to_history(self):
        current_state = self._model.clone()
        self._state_history.appendleft(current_state)