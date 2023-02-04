# articy3_renpy3
articy:draft 3 to Ren'Py 3 converter

The goal of this tool is to help visual novel creators to create most of their 
dialogue flow, interactions etc. in articy:draft 3 instead of writing rpy files directly.
This should make it easier to refactor the game and see how everything affects each other.

The tool can also convert character and variable definitions into Ren'Py readable format.

The tool handles only the most common use cases, and isn't meant to replace the actual
hard work needed to make the edge cases work.

## Flow conversion

Current the tool assumes the following structure:
1. Main dialogue level named according to the labels. Target filenames are in text field.
2. Dialogue fragments have speakers with lines. Any scene commands etc. are assumed to be in "stage direction" portion of the dialogue frament.



## Character conversion

To get the characters to export correctly, you need to set the CHARACTER_ENTITY 
to match the value of the Ren'Py character entity you've created in articy.
My default technical name is "RenCharacter".

If you want the converter to support color for the character, the current
code assumes the Ren'Py character has Template named 
"RenCharProps", which then has field named "Color".

## Variable conversion

In articy you need to define namespace in order to define global variables. articy3_renpy3 takes
these namespaces and converts them to python definitions verbatim so that variable x in
namespace flags will be defined as flags.x. Please note that the names and default values
are *NOT* converted in anyway.


![Example of global variable definition.](./imgs/global_variables.png)
