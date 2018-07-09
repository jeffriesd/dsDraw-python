from datastructures import tree
from drawtools import view
from screeninfo import get_monitors
from util import logging_util as log
from tkinter import Tk
import random
from util.my_threads import TestThread
from collections import deque
from time import sleep
from util.exceptions import InvalidCommandError
from command.sequence import CommandSequence


class DrawControl:
    def __init__(self, model=None, master=None, width=800, height=600):
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

        self.model = model
        self.model.ctrl = self
        self.model.set_logger(self.model_logger)
        self.model.set_control(self)

        # creating main view (subclass of tk.Frame)
        # and passing in data structure
        self.view = view.DrawApp(master=master, width=width, height=height,
                                 ds=model, control=self, logger=self.view_logger, background="#333")

        self.logger.info("\n\n\t----- new run -----\n")
        self.logger.info("created main view")

        # initialize command state
        self.last_command = None

        self.canvas = self.view.canvas

        # time in seconds for animation to occur
        self.tick = .1

        self.cell_w = -1
        self.cell_h = -1

        # use stack to keep track of command history
        self.command_history = deque(maxlen=10)

        # command sequence object initialized with reference to control class
        self.command_sequence = CommandSequence(self)


    def clear_log(self):
        """Open log and immediately close stream to empty file contents"""
        with open('../logs/control_log.log', 'w'):
            pass

    def parse_command(self, command_text):
        """Parses a command with the first argument being
            the command type e.g. 'insert', 'delete', 'clear'
            and the rest being arguments to the respective command"""
        spl = command_text.split(" ")
        command_type = spl[0]
        args = spl[1:]

        # get command factory and use it to instantiate parsed command
        my_command_factory = self.model.get_command_factory()
        # may raise Exception (InvalidCommandError) if syntax error in command text
        my_command = my_command_factory.create_command(command_type, *args)

        return my_command

    def perform_command(self, command):
        """Pass in a command which has been initialized with a receiver.
            Perform command by calling command.execute() and redraw the canvas
            if necessary"""

        self.logger.info("Performing %s on %s" % (command, command.receiver))
        self.command_history.appendleft(command)

        command.execute()

        if command.should_redraw:
            self.display()

    def process_command(self, command_text):
        """
        Parse and instantiate command with parse_command()
        and execute it with perform_command(), checking for
        syntactical and logical errors, and updating
        the console for the user.
        :param command_text: command text passed from view
        """
        # catch invalid command errors (KeyError from command_factory)
        # e.g. typing 'remov 39' into console
        try:
            command_obj = self.parse_command(command_text)

            # clear contents and add it to console
            self.view.console.add_line(command_text)

            # catch logical errors,
            # e.g. trying to remove a node which isn't there
            try:
                self.perform_command(command_obj)
            except Exception as ex:
                err_msg = "Error completing '%s': %s" % (command_text, ex)
                self.logger.warning(err_msg)
                self.view.console.add_line(err_msg, is_command=False)

        except InvalidCommandError as err:
            # still show commands with bad syntax
            self.view.console.add_line(command_text)

            err_msg = "Syntax error: %s" % err
            self.logger.warning(err_msg)
            self.view.console.add_line(err_msg, is_command=False)

    def undo_command(self):
        """Pass in a command which has been initialized with a receiver.
            Perform command by calling command.execute() and redraw the canvas
            if necessary"""
        last_command = self.command_history.popleft()
        self.logger.info("Undoing %s on %s" % (last_command, last_command.receiver))

        last_command.undo()

        if last_command.should_redraw:
            self.display()

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

        if do_render:
            self.model.render()

        # determine node sizes
        self.preprocess()

        self.view.clear_canvas()
        self.draw_on_canvas()

        if do_sleep:
            self.canvas.update()
            sleep(self.tick)

    def preprocess(self):
        """Determines relative sizes/aspect ratios of data structures"""
        pass

    def draw_on_canvas(self):
        """Performs specific logic to draw nodes/edges to canvas"""
        pass


class TreeDraw(DrawControl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger.info("using tree mode")
        self.tree = self.model
        self.root = self.tree.root

        self.test_thread = None

        self.view.mainloop()

    def set_ds(self, new_ds):
        self.model = new_ds
        self.tree = new_ds
        self.root = new_ds.root

    def duplicate_coords(self):
        all_xy = [(node.x, node.y) for node in self.root]
        all_1 = all([all_xy.count((node.x, node.y)) == 1 for node in self.root])
        if all_1:
            # print("only 1 of each coordinate!")
            return None
        else:
            # print("duplicate coordinates. BAD!!!!!")
            return [node for node in self.root
                    if all_xy.count((node.x, node.y)) != 1]

    def preprocess(self):
        self.logger.debug("entering preprocess stage")
        width = self.canvas.width
        height = self.canvas.height

        self.cell_w = width / (self.tree.max_x - self.tree.min_x + 1)
        self.cell_h = height / (self.tree.max_y - self.tree.min_y + 1)

        self.logger.debug("cell size set; width: %s, height: %s" % (self.cell_w, self.cell_h))

    def draw_on_canvas(self, circle=False):
        """
        Determines size of each cell to be drawn and
        iterates through tree, drawing edges first, then
        nodes in an inorder traversal.
        :param circle: if True, draw nodes as circles
        """
        # if circle set to True, then
        # pick smaller of width/height

        if circle:
            cell_w = cell_h = min(self.cell_w, self.cell_h)
        else:
            cell_w = self.cell_w
            cell_h = self.cell_h

        # traverse tree in preorder so lines get drawn
        # first and nodes are placed on top
        for node in self.root.preorder():
            x0 = node.x * cell_w
            y0 = node.y * cell_h
            for c in node.children():
                x1 = c.x * cell_w
                y1 = c.y * cell_h
                center_offsets = [cell_w/2, cell_h/2] * 2

                pts = [x0, y0, x1, y1]
                centers = [pt + off for pt, off in zip(pts, center_offsets)]

                # show color for bst property
                color = "blue" if c.val <= node.val else "red"
                color = "green" if c.val == node.val else color
                self.canvas.create_line(*centers, fill=color, width=2)

            # draw nodes at 50% size as to not block
            # drawing of edges
            x0_n, y0_n = [x0 + cell_w/4, y0 + cell_h/4]

            self.canvas.create_oval(x0_n, y0_n, x0_n + cell_w/2, y0_n + cell_h/2, fill=node.color)
            # node_text = ("%sCC:\n%i, %i\ns:%i, d:%i"
            #                               % (node, node.x, node.y,
            #                                  node.get_size(), node.depth))
            # node_text = ("%s\nd: %s; s: %s" % ("   " + str(node), node.depth, node.get_size()))
            # node_text = ("%s\nxl: %s, xr: %s\nd:%s; s:%s" % (node, node.xleft, node.xright, node.depth, node.get_size()))
            node_text = node
            # node_text = ""

            self.canvas.create_text(x0 + cell_w/2, y0 + cell_h/2,
                                    text=node_text)

    def test_dups(self):
        """Tests for duplicate coordinates"""
        while True:
            self.view.redraw()
            self.tree.render()
            self.preprocess()
            if self.duplicate_coords():
                # print("v, x, y, xleft, xright")
                # print([(node, node.x, node.y, node.xleft, node.xright) for node in self.duplicate_coords()])
                print(self.duplicate_coords())
                self.model.log("debug", "duplicates: %s" % self.duplicate_coords())
                print(list(self.root.preorder()))

                break
            else:
                print("all good")

        self.display()

    def continuous_test(self, sleep_time=.05):
        if not self.test_thread:
            self.test_thread = TestThread(target=self.view.redraw, sleep_time=sleep_time)
            self.test_thread.start()
        else:
            self.test_thread.stop()
            self.test_thread = None




def build_tree(n, max_val, t=None):
    """Builds a tree of unique integer elements"""
    t = tree.BST() if t is None else t
    max_val = max(max_val, n)
    r_set = random.sample(range(max_val), n)
    for x in r_set:
        t.insert(x)
    return t


def my_tree(size=0):
    t = tree.BST()

    nodes = [9, 6, 0, 3, 2, 1, 4, 5, 7, 8, 10, 14, 13, 12, 11]

    if size:
        nodes = random.sample(list(range(size)), size)

        # special easy case
        if size == 9:
            nodes = [4, 1, 5, 0, 2, 7, 3, 6, 8]

    for n in nodes:
        t.insert(n)
    return t


def main():
    # function from screeninfo library to
    # get screen dimensions
    dim = get_monitors()[0]
    width = dim.width
    height = dim.height

    t = my_tree()

    root = Tk()

    TreeDraw(t, root, width, height)

if __name__ == '__main__':
    main()
