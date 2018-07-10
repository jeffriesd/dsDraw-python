import tkinter as tk
from tkinter import Canvas, Button, Entry, font as tkfont
from controller import drawcontrol as ctrl
from command.bst_command import BSTInsertCommand, BSTRemoveCommand
from collections import deque
from textwrap import wrap
from util.exceptions import InvalidCommandError


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


class DrawApp(tk.Frame):
    def __init__(self, ds, control, *args, **kwargs):
        """
        Initializes width and height assuming that
        kwargs['width'/'height'] are the screen size
        :param ds: working data structure
        :param args: args for tk.Frame
        :param kwargs: kwargs for tk.Frame
        """
        self.ds = ds
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

        self.insert_button = Button(self, bg="#333", fg="white", text="Insert", command=self.ins_button_clicked)
        self.insert_button.place(relwidth=0.12, relheight=0.05, relx=0.05, rely=0.05)
        self.insert_input = Entry(self, bg="#ccc", fg="black")
        self.insert_input.place(relwidth=0.12, relheight=0.05, relx=0.18, rely=0.05)


        self.remove_button = Button(self, bg="#333", fg="white", text="Remove", command=self.rem_button_clicked)
        self.remove_button.place(relwidth=0.12, relheight=0.05, relx=0.05, rely=0.10)
        self.remove_input = Entry(self, bg="#ccc", fg="black")
        self.remove_input.place(relwidth=0.12, relheight=0.05, relx=0.18, rely=0.10)


        self.undo_button = Button(self, bg="#333", fg="white", text="Undo", command=self.control.undo_command)
        self.undo_button.place(relwidth=0.25, relheight=0.1, relx=0.05, rely=0.15)


        self.canvas = DrawCanvas(self, highlightthickness=0, bg="#ccc")
        # setting canvas to fill right side of screen -
        #   60% width, offset 20% left of center,
        #   so 40% total
        self.canvas.place(relwidth=0.6, relheight=0.9, relx=0.35, rely=0.05)

        self.d_button = Button(self, bg="#333", fg="white", text="Draw", command=self.redraw)
        self.d_button.place(relwidth=0.12, relheight=0.1, relx=0.05, rely=0.875)


        self.test_button = Button(self, bg="#333", fg="white", text="Test", command=self.control.continuous_test)
        self.test_button.place(relwidth=0.12, relheight=0.1, relx=0.18, rely=0.875)

    def redraw(self):
        # temporary code to reset tree each button press
        new_tree = ctrl.build_tree(50, 0)
        self.ds = new_tree
        self.ds.set_logger(self.control.model_logger)

        # bind data structure to control object
        self.ds.set_control(self.control)
        self.control.set_ds(self.ds)

        self.control.display()

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
        self.console.reset_cycle()

        self.control.process_command(command_text)

    def ins_button_clicked(self):
        value = int(self.insert_input.get())
        command = BSTInsertCommand(self.ds, value, change_color=True)

        # self.control.do_command(command)
        self.control.add_to_sequence(command)

    def rem_button_clicked(self):
        try:
            value = int(self.remove_input.get())
        except ValueError:
            value = self.ds.root.val
        command = BSTRemoveCommand(self.ds, value, change_color=True)

        # self.control.do_command(command)
        self.control.add_to_sequence(command)