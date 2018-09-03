from tkinter import Canvas, Entry, Text, WORD


class TextBox(Text):

    def __init__(self, parent, x_0, y_0, x_1, y_1, **kwargs):
        """
        Basic textbox class
        :param parent: parent canvas
        :param x_0: top left x
        :param y_0: top left y
        :param x_1: bottom right x
        :param y_1: bottom right y

        background, borderwidth, cursor,
            exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, padx, pady,
            relief, selectbackground,
            selectborderwidth, selectforeground,
            setgrid, takefocus,
            xscrollcommand, yscrollcommand,
        """
        super().__init__(parent, **kwargs)
        self.parent = parent

        # setting wrap to word level
        self.configure(wrap=WORD)

        # creating uniform border
        self.configure(highlightthickness=1)
        self.configure(highlightbackground="black")
        self.configure(borderwidth=0)

        self.width = (x_1 - x_0)
        self.height = (y_1 - y_0)

        # determine relative placement to parent canvas
        self.relwidth = self.width / parent.width
        self.relheight = self.height / parent.height

        self.x = x_0
        self.y = y_0

        self.place(relwidth=self.relwidth, relheight=self.relheight, x=self.x, y=self.y)

        self.bind("<Button-1>", self.clicked)
        self.bind("<B1-Motion>", self.move_text_box)
        self.bind("<B3-Motion>", self.resize_text_box)

        self.start_x = 0
        self.start_y = 0

    def clicked(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def move_text_box(self, event):
        """
        Use place geometry manager to move text box.
        """
        top_left_x = self.x + event.x - self.start_x
        top_left_y = self.y + event.y - self.start_y

        self.x = top_left_x
        self.y = top_left_y

        self.place(relwidth=self.relwidth, relheight=self.relheight, x=self.x, y=self.y)

    def resize_text_box(self, event):
        """
        Use place geometry manager to resize from bottom right corner.
        """
        self.width = event.x
        self.height = event.y
        self.relwidth = self.width / self.parent.width
        self.relheight = self.height / self.parent.height

        self.place(relwidth=self.relwidth, relheight=self.relheight, x=self.x, y=self.y)


class Annotator(object):

    def __init__(self, canvas):
        """
        Class to handle annotation of canvas object.
        Modes include Text and Arc.
        """
        self.canvas = canvas
        # add bindings for annotating canvas by clicking
        self.canvas.bind("<Button-1>", self.canvas_clicked)
        self.canvas.bind("<B1-Motion>", self.canvas_mouse_hold)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_mouse_released)

        self.new_text_rect_id = None

        self.start_x = 0
        self.start_y = 0

    def canvas_clicked(self, event):
        """
        Left-click pushed somewhere on canvas
        """
        self.start_x = event.x
        self.start_y = event.y

        # remove focus from any focused annotations
        self.canvas.master.master.focus()

    def canvas_mouse_hold(self, event):
        """
        Left-click being held while mouse moves on canvas.
        """
        # draw hollow rectangle from start of click
        # to current position
        if self.get_annotation_mode() == "text":
            self.canvas.delete(self.new_text_rect_id)
            self.new_text_rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y)

    def canvas_mouse_released(self, event):
        if self.get_annotation_mode() == "text":
            self.canvas.delete(self.new_text_rect_id)
            nex_text_box = TextBox(self.canvas, self.start_x, self.start_y,
                                   event.x, event.y, bg="white")

    def get_annotation_mode(self):
        """
        Ask parent canvas for annotation mode
        (terminates at CompositeCanvas).
        """
        return self.canvas.get_annotation_mode()