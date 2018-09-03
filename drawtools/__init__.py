from tkinter.font import Font

dsDraw_colors = {"red": "#e74c3c",
                 "pink": "#f1948a",
                 "orange": "#f39c12",
                 "yellow": "#f7dc6f",
                 "green": "#52be80",
                 "lightgreen": "#82e0aa",
                 "blue": "#2e86c1",
                 "lightblue": "#5dade2",
                 "purple": "#a569bd"}

def default_font():
    """
    Written as method because in order to create a Font
    object, there must be an instance of Tk() running
    """
    return Font(family="Monospace", size=10, weight="normal")