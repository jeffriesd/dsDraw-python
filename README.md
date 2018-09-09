# dsDraw

dsDraw is an interactive tool for drawing data structures for educational purposes. It uses an embedded python shell as a command line interface for creating data structures.

To display a data structure in the drawing area, create a new data structure variable e.g. `some_data_structure = BST(25)` and then enter the command `show some_data_structure`.
If the drawing area is already occupied, the current active pane will be split along its longer axis to make room for the new pane.

# Data Structures

  ### Array (one dimensional)
  Arrays are drawn as a series of adjacent square cells with white fill as default. If the array is too long and 
  the values won't fit inside the cells, the array is compressed to show only the beginning and end elements.
  To create a new array, provide an iterable of values or a number of elements to fill the array with random values.
  
  e.g.
  ```python
  a = Array(40)
  ```
  or 
  ```python
  a = Array(range(5, 25))
  ```
  
  To access or modify elements, use `array[index]` as if it were a python list.
  
  #### Commands
  * swap(i, j) -- 
    Visually swaps the elements at indices i and j.
  * color("c", i, j) --
    Colors elements i to j (inclusive) with the specified color. Currently supports the following colors: red, pink, orange, yellow, green, light green, blue, light blue, purple.
  * hide_values() -- toggles visibility of array values
  * hide_indices() -- toggles visibility of array indices
  * compress() -- toggles forced compression. If the array is already compressed because of its size, this won't do anything.
    
   ### BST (Binary Search Tree)
   To create a new bst, provide
# Hotkeys
* Control + Z: undo last operation
* Control + T: hide/show console
    
 
  
  
