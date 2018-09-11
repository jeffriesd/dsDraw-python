from controller import drawcontrol as dc
from tkinter import Tk

def main():
    # function from screeninfo library to
    # get screen dimensions
    # dim = get_monitors()[0]
    # width = dim.width
    # height = dim.height

    root = Tk()

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    d = dc.DrawControl(root, width, height)
    d.view.mainloop()


if __name__ == '__main__':
    main()