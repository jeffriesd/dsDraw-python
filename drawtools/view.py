import tkinter as tk
from tkinter import Canvas, Button, Entry, font as tkfont
from controller import drawcontrol as ctrl
from command.bst_command import BSTInsertCommand, BSTRemoveCommand
from collections import deque
from textwrap import wrap


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

        y_spacing = self.font['size'] * 2
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

                    # only show >> for commands
                    if console_line.is_command:
                        line = ">> " + line
                else:
                    # offset wrapped lines
                    x = self.font.measure(">>  ")

                self.create_text(x, y, text=line, anchor='w', font=self.font)
                y -= y_spacing


class DrawCanvas(Canvas):
    """
    Main view to draw data structures.
    Extends from tk.Canvas and is self resizing
    with a binding to <Configure>. This is necessary
    to resize the objects within the canvas (tree, graph, etc)
    """
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

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

    def get_focused_child(self):
        for _, canvas in self.children.items():
            if canvas.focused:
                return canvas

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

        self.mono_font = tkfont.Font(family="Monospace", size=10, weight="normal")
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
        self.console_input.place(relwidth=0.25, relheight=0.05, relx=0.05, rely=0.8)
        self.console_input.bind("<Return>", self.command_entered)

        # initialize Console with reference to input
        self.console = Console(self, self.console_input, bg="white")
        self.console.place(relwidth=0.25, relheight=0.75, relx=0.05, rely=0.05)

        # bind up/down arrow keys to console action
        self.console_input.bind("<Up>", self.console.previous_command)
        self.console_input.bind("<Down>", self.console.next_command)
        self.console_input.bind("<Control-c>", self.console.clear_input)
        # bind Ctrl z to undo action
        self.console_input.bind("<Control-z>", self.control.undo_command)

        self.undo_button = Button(self, bg="#333", fg="white", text="Undo", command=self.control.undo_command)
        self.undo_button.place(relwidth=0.25, relheight=0.1, relx=0.05, rely=0.05)


        self.canvas = CompositeCanvas(self, highlightthickness=1, highlightbackground="black", bg="#ccc")
        # setting canvas to fill right side of screen -
        #   60% width, offset 20% left of center,
        #   so 40% total
        self.canvas.place(relwidth=0.6, relheight=0.9, relx=0.35, rely=0.05)

        self.d_button = Button(self, bg="#333", fg="white", text="Draw", command=None)
        self.d_button.place(relwidth=0.12, relheight=0.1, relx=0.05, rely=0.875)

        self.test_button = Button(self, bg="#333", fg="white", text="Test", command=None)
        self.test_button.place(relwidth=0.12, relheight=0.1, relx=0.18, rely=0.875)

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

        self.control.process_command(command_text)
