import tkinter as tk
from tkinter import Canvas, Button, Entry, font as tkfont
from drawtools import default_font
from drawtools.annotations import Annotator
from controller import drawcontrol as ctrl
from command.bst_command import BSTInsertCommand, BSTRemoveCommand
from collections import deque, defaultdict
from textwrap import wrap
from functools import partial


class AnnotationButton(Button):

    def __init__(self, parent, **kwargs):
        """
        Special button to change annotation modes.
        """
        super().__init__(parent, **kwargs)

        self.active = False

        self.bind("<Button-1>", self.toggle)

    def toggle(self, event):
        self.active = not self.active

        bg = "#ccc" if self.active else "#333"
        fg = "#333" if self.active else "#ccc"

        self.configure(bg=bg, fg=fg)

class Console(Canvas):
    """
    Canvas-like class to show command history. Command history
    will be stored in a stack and drawn top-up.
    New commands will be pushed on top, so the bottom of the console
    is the top of this stack.
    """

    class ConsoleLine(object):
        """
        Solely used to differentiate between commands and errors
        in cycling through commands and printing them.
        """
        def __init__(self, text, is_command):
            # super().__init__(text)
            self.text = str(text)
            self.is_command = is_command

        def __repr__(self):
            return self.text

    def __init__(self, parent, console_input, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.input = console_input

        # used to keep track of all ConsoleLine objects
        self.console_history = deque()
        # used only to track command objects (for cycling with keys)
        self.command_history = deque()

        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", lambda ev: self.input.focus())

        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.font = parent.mono_font

        # defaults for text resizing
        self.chars_per_line = 35
        self.lines_per_console = 45

        # store index for cycling through commands with arrow keys
        self.cycle_index = -1

        self.seq_mode = False

        # flag used to toggle visibility
        self.hidden = False

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self.relx = kwargs["relx"]
        self.rely = kwargs["rely"]
        self.relwidth = kwargs["relwidth"]
        self.relheight = kwargs["relheight"]

    def on_resize(self, event):
        """
        Function to automatically update
        canvas width/height and scale its
        components when it gets resized.
        Also scales font to fit 45 characters.
        """
        nwidth = event.width
        nheight = event.height
        self.config(width=nwidth, height=nheight)
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.scale("all", 0, 0, wscale, hscale)
        self.width = nwidth
        self.height = nheight

        # if width / m_width should = 35,
        # ~35 characters should fit on one line
        m_width = self.font.measure("m")
        font_ratio_x = nwidth / m_width
        font_scale_factor_x = font_ratio_x / self.chars_per_line
        new_font_size_x = int(self.font['size'] * font_scale_factor_x)

        # if height / m_width should = 45,
        # there should be ~45 lines without spacing,
        # so about 20-25 with spacing
        font_ratio_y = nheight / m_width
        font_scale_factor_y = font_ratio_y / self.lines_per_console
        new_font_size_y = int(self.font['size'] * font_scale_factor_y)

        self.font.configure(size=min(new_font_size_x, new_font_size_y))

    def reset_cycle(self):
        """Used to reset cycle when command is entered from
            using arrow key history."""
        self.cycle_index = -1

    def clear_input(self, event=None):
        self.input.delete(0, "end")

    def clear_console(self, event=None):
        self.delete("all")
        # calling clear on deque, but command history still exists
        # for cycling with arrow keys
        self.console_history.clear()

    def previous_command(self, event=None):
        """Function to support quick cycling of last command by
            putting it back into the console Entry.
            Bound to up arrow key by default"""
        self.cycle_index += 1
        if self.cycle_index >= len(self.command_history):
            self.cycle_index = len(self.command_history) - 1

        last_command = self.command_history[self.cycle_index]
        self.clear_input()
        self.input.insert(0, last_command)

    def next_command(self, event=None):
        """Function to support quick cycling of commands in
            the forwards direction. Bound to down arrow key
            by default. If 'bottom' is hit and arrow key pressed
            again, then clear the input"""

        self.cycle_index -= 1
        if self.cycle_index < 0:
            self.cycle_index = -1
            self.clear_input()
        else:
            last_command = self.command_history[self.cycle_index]
            self.clear_input()
            self.input.insert(0, last_command)

    def add_line(self, command_text, is_command=True):
        """Adds a line of text to console history.
            Note that this is a string and not the actual command objects,
            so may include things like 'syntax error'"""
        new_line = Console.ConsoleLine(command_text, is_command)
        if is_command:
            self.command_history.appendleft(new_line)
        self.console_history.appendleft(new_line)
        self.redraw()

    def last_line(self):
        return self.command_history[-1]

    def update(self):
        """
        Overriding update so font size gets updated
        on parent canvas resize
        """
        super().update()
        self.redraw()

    def redraw(self):
        """Delete previous contents of canvas and redraw
            command history with the top of the stack at
            the bottom of the console"""
        self.delete("all")

        y_spacing = self.font.measure("_") * 3
        y = self.winfo_height() - y_spacing

        for console_line in self.console_history:
            # grab text from console_line object
            line_text = console_line.text

            # break longer strings into line-sized chunks
            line_wrapped = wrap(line_text, self.chars_per_line - 5)

            # lines have to be drawn in reverse since bottom of console
            # should be the end of the command
            for line in reversed(line_wrapped):
                if line == line_wrapped[0]:
                    # show separator for each new command
                    x = self.font.measure(" ")

                    if self.seq_mode:
                        x = self.font.measure("   ")

                    # only show >> for commands
                    if console_line.is_command:
                        line = ">> " + line
                else:
                    # offset wrapped lines
                    x = self.font.measure(">>  ")

                self.create_text(x, y, text=line, anchor='w', font=self.font)
                y -= y_spacing

    def sequence_mode(self, mode):
        self.seq_mode = mode


class DrawCanvas(Canvas):
    """
    Main view to draw data structures.
    Extends from tk.Canvas and is self resizing
    with a binding to <Configure>. This is necessary
    to resize the objects within the canvas (tree, array, etc)
    """
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

        self.annotator = Annotator(self)

    def on_resize(self, event):
        """
        Function to automatically update
        canvas width/height and scale its
        components when it gets resized
        """
        nwidth = event.width
        nheight = event.height
        self.config(width=nwidth, height=nheight)
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.scale("all", 0, 0, wscale, hscale)
        self.width = nwidth
        self.height = nheight

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self.relx = kwargs["relx"]
        self.rely = kwargs["rely"]
        self.relwidth = kwargs["relwidth"]
        self.relheight = kwargs["relheight"]

    def get_geometry(self):
        return self.relx, self.rely, self.relwidth, self.relheight

    def get_annotation_mode(self):
        """
        Ask parent for annotation mode (will terminate at CompositeCanvas)
        """
        return self.parent.get_annotation_mode()


class CompositeCanvas(DrawCanvas):
    """
    Composite class to handle drawing multiple canvasses
    on the screen for multiple data structures.
    All method calls are simply passed to all _children.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.control = self.parent.control
        self.kwargs = kwargs

    def update(self):
        for name, c in self.children.items():
            c.update()
        super().update()

    def update_child(self, name):
        self.children[name].update()

    def get_child(self, name):
        return self.children[name]

    def new_child(self, name):
        """
        Create new canvas and return it, passing
        in same kwargs that CompositeCanvas receives.
        Geometry is calculated by splitting the most
        recent child in half.
        :param name:
        :param new_canvas:
        :return:
        """
        new_canvas = DrawCanvas(self, name=name, **self.kwargs)
        focused_render = self.control.get_focused()

        if focused_render:
            focused_canvas = focused_render.canvas
            self.split_canvas(focused_canvas, new_canvas)
        else:
            new_canvas.place(relx=0, rely=0,
                             relwidth=1, relheight=1)

        return new_canvas

    def split_canvas(self, focused_canvas, new_canvas):
        """
        Split focused canvas along longer axis, place it in its
        new relative position and place the new canvas beside it
        """
        rel_x, rel_y, rel_width, rel_height = focused_canvas.get_geometry()
        true_height = focused_canvas.height
        true_width = focused_canvas.width

        # split along wider axis
        if true_width > true_height:
            _rel_width = rel_width / 2

            # resize last child
            focused_canvas.place(relx=rel_x, rely=rel_y, relwidth=_rel_width, relheight=rel_height)

            # place new canvas
            new_canvas.place(relx=rel_x + _rel_width, rely=rel_y,
                             relwidth=_rel_width, relheight=rel_height)
        else:
            _rel_height = rel_height / 2

            focused_canvas.place(relx=rel_x, rely=rel_y, relwidth=rel_width, relheight=_rel_height)
            new_canvas.place(relx=rel_x, rely=rel_y + _rel_height,
                             relwidth=rel_width, relheight=_rel_height)

    def get_annotation_mode(self):
        """Ask DrawApp for annotation mode"""
        return self.parent.annotation_mode


class DrawApp(tk.Frame):
    def __init__(self, control, *args, **kwargs):
        """
        Initializes width and height assuming that
        kwargs['width'/'height'] are the screen size
        :param ds: working data structure
        :param args: args for tk.Frame
        :param kwargs: kwargs for tk.Frame
        """
        self.control = control

        self.screen_width = kwargs["width"]
        self.screen_height = kwargs["height"]
        self.width = self.screen_width * 0.75
        self.height = self.screen_height * 0.75
        super().__init__(*args, **kwargs)

        # resizing frame to 0.75 x 0.75 size
        # (could have changed args before calling super()
        # to accomplish this, but then the frame would have
        # a maximum size of 75% x 75% and couldn't fill the entire screen)
        self.master.geometry("%ix%i" % (self.width, self.height))
        self.pack()
        self.bind("<Configure>", self.on_resize)

        # one annotation mode for entire application
        self.annotation_mode = None
        self.annotation_buttons = {}

        self.mono_font = default_font()
        self.init_components()

    def set_logger(self, logger):
        self.logger = logger
        self.clear_log()
        self.logger.info("\n\n\t----- new run -----\n")

    def clear_log(self):
        with open("../logs/view_log.log", "w"):
            pass

    def on_resize(self, event):
        """Updates width/height and redraws canvas on resize"""
        self.width = event.width
        self.height = event.height
        self.control.display()

        for name, child_canvas in self.children.items():
            child_canvas.update()

    def init_components(self):
        """
        Uses Tkinter place layout manager to set
        relative sizes for components. Binds 'draw'
        button to self.display()
        """

        self.console_input = Entry(self, bg="white", borderwidth=0,
                                   highlightbackground="white", highlightcolor="white",
                                   font=self.mono_font)
        self.console_input.place(relwidth=0.25, relheight=0.05, relx=0.05, rely=0.9)
        self.console_input.bind("<Return>", self.command_entered)

        # initialize Console with reference to input
        self.console = Console(self, self.console_input, bg="white")
        self.console.place(relwidth=0.25, relheight=0.85, relx=0.05, rely=0.05)

        # bind up/down arrow keys to console action
        self.console_input.bind("<Up>", self.console.previous_command)
        self.console_input.bind("<Down>", self.console.next_command)
        self.console_input.bind("<Control-c>", self.console.clear_input)
        # bind Ctrl z to undo action
        self.console_input.bind("<Control-z>", self.control.process_undo)

        self.canvas = CompositeCanvas(self, highlightthickness=1, highlightbackground="black", bg="#ccc")
        # setting canvas to fill right side of screen -
        #   60% width, offset 20% left of center,
        #   so 40% total
        self.canvas.place(relwidth=0.6, relheight=0.9, relx=0.35, rely=0.05)

        # add annotation buttons
        text_mode = partial(self.toggle_annotation_mode, "text")
        self.text_annotation_button = AnnotationButton(self, text="text", bg="#333", fg="white", command=text_mode)
        self.text_annotation_button.place(relwidth=0.04, relheight=0.04, relx=0.955, rely=0.055)

        self.annotation_buttons["text"] = self.text_annotation_button

        # click root window to get focus
        self.bind("<Button-1>", lambda ev: self.focus_set())

        # toggle console while console has focus or root window has focus
        self.bind("<Control-t>", self.toggle_console)
        self.console_input.bind("<Control-t>", self.toggle_console)


    def clear_canvas(self):
        self.canvas.delete("all")

    def command_entered(self, event):
        """
        Command entered into input, so parse it,
        show it in console and clear the current input.
        Then pass it to control for execution and add it to the console history.
        """

        command_text = self.console_input.get()
        self.logger.info("'%s' entered into command prompt." % command_text)
        self.console.clear_input()
        # reset arrow key cycle
        self.console.reset_cycle()
        self.console.add_line(command_text)

        self.control.process_command(command_text)

    def toggle_annotation_mode(self, mode):
        if self.annotation_mode == mode:
            self.annotation_mode = None
        else:
            self.annotation_mode = mode

    def toggle_console(self, event):
        """Hide/show console"""

        if self.console.hidden:
            self.console.place(relwidth=0.25, relheight=0.85, relx=0.05, rely=0.05)
            self.canvas.place(relwidth=0.6, relheight=0.9, relx=0.35, rely=0.05)
        else:
            self.canvas.place(relwidth=self.canvas.relwidth + self.console.relwidth + 0.05,
                              relheight=self.canvas.relheight,
                              relx=self.console.relx, rely=self.console.rely)

            self.console.place(relwidth=0, relheight=0, relx=0, rely=0)

        self.console.hidden = not self.console.hidden



