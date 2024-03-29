from tkinter import Canvas, Entry, Text, WORD, LAST
from drawtools import default_font


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
        self.font = default_font()
        kwargs["font"] = self.font

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
        self.bind("<Control-B1-Motion>", self.move_text_box)
        self.bind("<B3-Motion>", self.resize_text_box)

        self.start_x = 0
        self.start_y = 0

    def clicked(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.lift()

        if self.parent.get_annotation_mode() == "erase":
            self.delete_annotation()

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

    def delete_annotation(self):
        self.destroy()


class ArrowPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Arrow(object):
    def __init__(self, parent, x_0, y_0, x_1, y_1, **kwargs):
        self.parent = parent
        self.kwargs = kwargs

        # temporary line should be gray
        self.temp_kwargs = {k: v for k, v in kwargs.items()}
        self.temp_kwargs["fill"] = "gray"

        self.p_1 = ArrowPoint(x_0, y_0)
        self.p_2 = ArrowPoint((x_1 + x_0) / 2, (y_1 + y_0) / 2)
        self.p_3 = ArrowPoint(x_1, y_1)

        # save id for moving
        self.tk_id = self.parent.create_line(self.p_1.x, self.p_1.y, self.p_2.x, self.p_2.y,
                                             self.p_3.x, self.p_3.y, smooth=True, arrow=LAST, **kwargs)

        self.straight = True

        self.temp_id = None

        self.bind_events()

    def delete_annotation(self):
        self.parent.delete(self.tk_id)

    def bind_events(self):
        # tag_bind(item, event=None, callback, add=None)
        self.parent.tag_bind(self.tk_id, "<Button-1>", self.clicked)
        self.parent.tag_bind(self.tk_id, "<Control-B1-Motion>", self.translate_arrow)
        self.parent.tag_bind(self.tk_id, "<B1-Motion>", self.move_point)
        self.parent.tag_bind(self.tk_id, "<ButtonRelease-1>", self.release_point)

    def clicked(self, event):
        self.start_x = event.x
        self.start_y = event.y

        self.parent.tag_raise(self.tk_id)

        # assign closest point to click for re-aligning arc
        self.moving_point = self.get_point(event.x, event.y)

        if self.parent.get_annotation_mode() == "erase":
            self.delete_annotation()

    def print_points(self):
        print("p1 = %s, %s; p2 = %s, %s; p3 = %s, %s"
              % (self.p_1.x, self.p_1.y, self.p_2.x, self.p_2.y, self.p_3.x, self.p_3.y))

    def move_point(self, event):
        """
        Realign arrow by moving endpoints or middle point.
        Straight lines are redrawn differently than curves.
        (moving an endpoint of a straight line results in a straight line)
        Straightness is reevaluated after realignment is complete.
        """

        if self.moving_point:
            self.moving_point.x = event.x
            self.moving_point.y = event.y

            # delete and redraw arrow with new curvature
            self.parent.delete(self.temp_id)

            # redraw straight line
            if not self.straight or self.moving_point is self.p_2:
                self.temp_id = self.parent.create_line(self.p_1.x, self.p_1.y, self.p_2.x, self.p_2.y,
                                                       self.p_3.x, self.p_3.y, smooth=True, arrow=LAST,
                                                       **self.temp_kwargs)
                self.straight = self.is_straight()
            elif self.straight:
                self.temp_id = self.parent.create_line(self.p_1.x, self.p_1.y,
                                        self.p_3.x, self.p_3.y, smooth=False, arrow=LAST, **self.temp_kwargs)

    def release_point(self, event):
        """
        Finish realigning arrow.
        """
        # delete temporary arrow
        self.parent.delete(self.temp_id)
        # delete original arrow
        self.parent.delete(self.tk_id)
        # remove original arrow id from annotations set
        self.parent.annotator.annotation_ids.remove(self.tk_id)


        # redraw updated line
        if self.straight:
            self.tk_id = self.parent.create_line(self.p_1.x, self.p_1.y,
                                             self.p_3.x, self.p_3.y, smooth=True, arrow=LAST, **self.kwargs)
        else:
            self.tk_id = self.parent.create_line(self.p_1.x, self.p_1.y, self.p_2.x, self.p_2.y,
                                                 self.p_3.x, self.p_3.y, smooth=True, arrow=LAST, **self.kwargs)

        self.bind_events()

        # replace tk_id in parent canvas.annotator.annotation_ids
        self.parent.annotator.annotation_ids.add(self.tk_id)

    def translate_arrow(self, event):
        """Move arrow by dragging"""
        self.parent.lift(self.tk_id)
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.parent.move(self.tk_id, dx, dy)

        self.start_x = event.x
        self.start_y = event.y

        # update points
        self.update_points(dx, dy)


    def update_points(self, dx, dy):
        """
        Updates point coordinates after translation
        """
        self.p_1.x += dx
        self.p_1.y += dy
        self.p_2.x += dx
        self.p_2.y += dy
        self.p_3.x += dx
        self.p_3.y += dy

    def get_point(self, x, y):
        """
        Returns closest point (euclidean) to coordinates (x, y)
        """
        euclidean_dist = lambda p: ((p.x - x) ** 2 + (p.y - y) ** 2) ** .5
        return min([self.p_1, self.p_2, self.p_3], key=euclidean_dist)

    def is_straight(self):
        """
        Returns true if line is straight
        (similar slopes between endpoints and endpoint to midpoint)
        """
        slope = lambda p1, p2: (p2.y - p1.y) / (p2.x - p1.x)
        true_slope = slope(self.p_1, self.p_3)
        mid_slope = slope(self.p_1, self.p_2)

        # allow mild difference in slope to be considered straight
        # (causes snap to straight line)
        return abs(true_slope - mid_slope) < .05


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
        self.new_arrow_id = None

        self.start_x = 0
        self.start_y = 0

        # keep track of annotation ids so they
        # don't get removed on clear_canvas()
        self.annotation_ids = set()

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

        current_mode = self.get_annotation_mode()
        # draw hollow rectangle from start of click
        # to current position
        if current_mode == "text":
            self.canvas.delete(self.new_text_rect_id)
            self.new_text_rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y)
        elif current_mode == "arrow":
            self.canvas.delete(self.new_arrow_id)
            self.new_arrow_id = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y)

    def canvas_mouse_released(self, event):
        current_mode = self.get_annotation_mode()

        # create a new annotation object
        if current_mode == "text":
            self.canvas.delete(self.new_text_rect_id)

            # dont allow text boxes smaller than 25x25 pixels
            if abs(self.start_x - event.x) > 25 and abs(self.start_y - event.y) > 25:
                new_textbox = TextBox(self.canvas, self.start_x, self.start_y,
                                       event.x, event.y, bg="white")
                self.annotation_ids.add(new_textbox)

        elif current_mode == "arrow":
            self.canvas.delete(self.new_arrow_id)
            new_arrow = Arrow(self.canvas, self.start_x, self.start_y, event.x, event.y,
                              fill="black", width=4)
            self.annotation_ids.add(new_arrow.tk_id)

    def get_annotation_mode(self):
        """
        Ask parent canvas for annotation mode
        (terminates at CompositeCanvas).
        """
        return self.canvas.get_annotation_mode()