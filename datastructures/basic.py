import logging
import util.logging_util as log
from copy import copy
from collections import deque


class DataStructure(object):

    def __init__(self):
        self.state_history = deque(maxlen=10)

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

    def add_state_to_history(self):
        current_state = self.clone()
        self.state_history.appendleft(current_state)

    def clone(self):
        raise NotImplementedError("Clone not implemented for %s" % self)

