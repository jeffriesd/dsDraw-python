from tkinter import Frame, Label
from tkinter.ttk import Combobox
from drawtools.colors import *

class AnnotationMenu(Frame):
    def __init__(self, parent, *args, **kwargs):
        # save place for original values
        self.relx = None
        self.rely = None
        self.relwidth = None
        self.relheight = None

        super().__init__(parent, *args, **kwargs)

        # keep reference to child_menu for destroying it
        self.child_menu = None

        # start in hidden state
        self.hide_menu()


    def place(self, *args, **kwargs):
        """
        Save original relwidth, relheight, relx, rely
        """
        super().place(*args, **kwargs)

        # save values first time only
        if None in [self.relx, self.rely, self.relwidth, self.relheight]:
            try:
                self.relx = kwargs["relx"]
                self.rely = kwargs["rely"]
                self.relwidth = kwargs["relwidth"]
                self.relheight = kwargs["relheight"]
            except KeyError:
                pass

    def show_menu(self, annotation_obj, annotation_class):
        """
        Supporting menus for arrow and text boxes
        """

        # set active menu bg
        self.configure(bg=ACTIVE_MENU)
        self.place(relx=self.relx, rely=self.rely, relwidth=self.relwidth, relheight=self.relheight)

        if annotation_class == "Arrow":
            self.child_menu = ArrowMenu(self, annotation_obj)
        elif annotation_class == "Text":
            pass

    def hide_menu(self):
        # hide with place relwidth, relheight=0
        self.place(relwidth=0, relheight=0)

        if self.child_menu:
            self.child_menu.destroy()


class ArrowMenu(object):
    def __init__(self, parent_menu, arrow_obj):
        """
        Abstraction to create a new specific instance of menu
        for some particular Arrow object
        :param parent_menu: singular AnnotationMenu
        """
        self.parent_menu = parent_menu
        self.arrow_obj = arrow_obj

        self.place_options()

    def place_options(self):
        """
        Draw all the OptionMenus needed
        to configure Arrows
        """
        current_config = self.arrow_obj.get_attributes()

        # place dash submenu
        dash_options = "dash", "solid"
        current_dash = current_config["dash"]
        self.dash_option = Combobox(self.parent_menu, state="readonly", value=dash_options)
        self.dash_option.set(str(current_dash))
        self.dash_option.bind("<<ComboboxSelected>>", self.set_dash)
        self.dash_option.place(relx=0.8,rely=0.5,relwidth=.2, relheight=0.5)

        # place dash label
        self.dash_label = Label(self.parent_menu, text="Dash/Solid", bg=ACTIVE_MENU, fg=ACTIVE_TEXT)
        self.dash_label.place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.5)

    def set_dash(self, event=None):
        state = self.dash_option.get()

        if state == "dash":
            self.arrow_obj.dash = (10, 10)
        elif state == "solid":
            self.arrow_obj.dash = None

        self.arrow_obj.create_arrow()

    def destroy(self):
        """
        Destroy all the OptionMenus created by this submenu
        :return:
        """
        self.dash_option.destroy()

