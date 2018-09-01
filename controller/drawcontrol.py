from datastructures import tree
from drawtools import view
from screeninfo import get_monitors
from util import logging_util as log
from tkinter import Tk
import random
from util.my_threads import CommandThread
from functools import partial
from collections import deque
from time import sleep
from command.command_factory import ControlCommandFactory
from util.exceptions import InvalidCommandError
from command.sequence import CommandSequence
from command import ModelCommand
from controller.environment import VariableEnvironment


class DrawControl:
    def __init__(self, master=None, width=800, height=600):
        """
        Constructor for main controller class
        :param model: data structure being drawn
        :param master: tk root window
        :param width: screen width
        :param height: screen height
        """
        # creating loggers
        self.logger = log.create_logger("control_logger", "debug", "../logs/control_log.log")
        self.view_logger = log.create_logger("view_logger", "debug", "../logs/view_log.log")
        self.model_logger = log.create_logger("model_logger", "debug", "../logs/model_log.log")

        # clear logging file
        self.clear_log()

        # creating main view (subclass of tk.Frame)
        # and passing in data structure
        self.view = view.DrawApp(master=master, width=width, height=height,
                                 control=self, background="#333")
        self.view.set_logger(self.view_logger)

        self.logger.info("\n\n\t----- new run -----\n")
        self.logger.info("created main view")

        # use stack to keep track of command history
        self.command_history = deque()

        # use dictionary to store user-defined variables
        self.my_variables = VariableEnvironment(self)

        # use dictionary to store render objects for redrawing
        self.my_renders = {}

    def add_model_to_view(self, model_name):
        """
        Assume a model has already been instantiated and
        assigned a name. Raises exception if name
        already assigned.
        :param model:
        :return:
        """
        if model_name in self.my_renders:
            raise Exception("Model '%s' already assigned to a render object" % model_name)

        my_model = self.my_variables[model_name]
        my_model.set_control(self)
        my_model.set_name(model_name)
        my_model.set_logger(self.model_logger)

        # create a new canvas and
        # corresponding render object
        new_canvas = self.view.canvas.new_child(model_name)

        # add click to raise functionality
        new_canvas.bind("<Button-1>", lambda ev: self.give_focus(model_name))

        render_class = my_model.get_render_class()
        my_render = render_class(my_model, new_canvas, name=model_name)

        # bind render object to name
        self.my_renders[model_name] = my_render

        self.give_focus(model_name)

    def give_focus(self, render):
        """
        Gives focus to a render object based on name
        or by passing on the object itself
        """
        for name, render_obj in self.my_renders.items():
            render_obj.focused = (name == render) or (render_obj == render)
        self.display(do_render=False)

    def get_focused(self):
        for name, render_obj in self.my_renders.items():
            if render_obj.focused:
                return render_obj

    def clear_log(self):
        """Open log and immediately close stream to empty file contents"""
        with open('../logs/control_log.log', 'w'):
            pass

    def parse_command(self, command_text):
        """Parses a command with the first argument being
            the command type e.g. 'insert', 'delete', 'clear'
            and the rest being arguments to the respective command.

            Assume receiver is control unless '.' present in first word
            in which case it's a command on a data structure.
            """

        spl = command_text.split(" ")

        # handle special case for command on model
        if "." in spl[0]:
            model_name, command_text = command_text.split(".")
            model = self.my_variables[model_name]
            my_command_factory = model.get_command_factory()
            self.give_focus(model_name)
        else:
            my_command_factory = ControlCommandFactory(self)

        spl = command_text.split(" ")
        command_type = spl[0]
        args = spl[1:] if len(spl) > 1 else []

        # parse args -- hack -- need to handle in another class
        def parse_args(arg):
            if ":" in arg:
                return self.my_variables[arg]
            return arg
        args = list(map(parse_args, args))
        print("command = %s; args = %s" % (command_text, args))

        # may raise Exception (InvalidCommandError) if syntax error in command text
        my_command = my_command_factory.create_command(command_type, *args)

        return my_command

    def raise_cmd_ex(self, ex, text):
        """Workaround to raise exception from spawned thread"""
        err_msg = "Error completing '%s': %s" % (text, ex)
        self.logger.warning(err_msg)

        self.view.console.add_line(err_msg, is_command=False)
        raise ex

    def process_command(self, command_text):
        """
        Parse and instantiate command with parse_command()
        and execute it with perform_command(), checking for
        syntactical and logical errors, and updating
        the console for the user.
        :param command_text: command text passed from view
        :return: return value in the case of commands like bst.find()
        """
        # catch invalid command errors (KeyError from command_factory)
        # e.g. typing 'remov 39' into console
        try:
            command_obj = self.parse_command(command_text)

            # catch logical errors,
            # e.g. trying to remove a node which isn't there
            try:
                cmd = partial(self.perform_command, command_obj)
                t = CommandThread(target=cmd, text=command_text,caller=self)
                ret_value = t.start()

                # add it to command history for undoing
                self.command_history.appendleft(command_obj)

                return ret_value
            except Exception as ex:
                err_msg = "Error completing '%s': %s" % (command_text, ex)
                self.logger.warning(err_msg)

                self.view.console.add_line(err_msg, is_command=False)
                raise(ex)

        except InvalidCommandError as err:

            err_msg = "Syntax error: %s" % err
            self.logger.warning(err_msg)
            self.view.console.add_line(err_msg, is_command=False)

    def perform_command(self, command_obj):
        """
        Pass in a command_obj which has been initialized with a receiver.
        Perform command_obj by calling command_obj.execute() and redraw the canvas
        if necessary.

        :return: return in case of commands like bst.find()
        """

        self.logger.info("Performing %s on %s" % (command_obj, command_obj.receiver))

        command_value = command_obj.execute()

        if command_obj.should_redraw:
            if not isinstance(command_obj, ModelCommand):
                self.display(do_sleep=False)
            else:
                # show animations and only update
                # relevant canvas
                try:
                    render_obj = self.my_renders[command_obj.receiver.name]

                    ##### need to add do_render as parameter #####

                    render_obj.display(do_render=command_obj.do_render)
                except KeyError:
                    raise Exception("Error updating canvas for '%s'. No corresponding render object" % command_obj.receiver)

        return command_value

    def process_undo(self, event=None):
        """
        Gets most recent command from command_history deque
        and start a new thread to perform the undo/redraw
        """
        try:
            last_command = self.command_history.popleft()
            undo_text = "Undoing '%s' on %s" % (last_command, last_command.receiver)
            self.logger.info(undo_text)

            # start new thread to perform undo
            perform_undo = partial(self.perform_undo, last_command)
            undo_thread = CommandThread(target=perform_undo, text=undo_text,caller=self)
            undo_thread.start()

            self.view.console.add_line(undo_text, is_command=False)

        except IndexError as e:
            err_msg = "Error: Nothing left to undo"
            self.logger.error(err_msg)
            self.view.console.add_line(err_msg, is_command=False)

    def perform_undo(self, last_command):
        """
        Encapsulates performance of undo command including redrawing
        of specific canvas. Intended to be run from a separate thread,
        created in process_undo
        """
        last_command.undo()
        if last_command.should_redraw:
            if last_command.receiver is self:
                self.display(do_sleep=False)
            else:
                # show animations and only update
                # relevant canvas
                try:
                    render_obj = self.my_renders[last_command.receiver.name]
                    render_obj.display()
                except KeyError:
                    raise Exception("Error updating canvas for '%s'. No corresponding render object" % last_command.receiver)


    def add_to_sequence(self, command_obj):
        """
            ***To be replaced by command object with control as receiver
        """
        self.command_sequence.add_command(command_obj)

    def do_full_sequence(self):
        """
            ***To be replaced by command object with control as receiver
        """
        self.command_sequence.execute_sequence()

    def set_ds(self, new_ds):
        self.model = new_ds

    def display(self, do_render=True, do_sleep=False):
        """Renders data structure (preprocess),
            clears canvas, and draws to canvas
            :param do_render - flag whether to run render algorithm again or not
            :param do_sleep - flag whether to pause for animation purposes or not"""
        for _, render in self.my_renders.items():
            render.display(do_render, do_sleep)


def main():
    # function from screeninfo library to
    # get screen dimensions
    dim = get_monitors()[0]
    width = dim.width
    height = dim.height

    root = Tk()

    d = DrawControl(root, width, height)
    d.view.mainloop()

if __name__ == '__main__':
    main()
