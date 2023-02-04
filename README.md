# articy3_renpy3
articy:draft 3 to Ren'Py 3 converter

The goal of this tool is to help visual novel creators to create most of their 
dialogue flow, interactions etc. in articy:draft 3 instead of writing rpy files directly.
This should make it easier to refactor the game and see how everything affects each other.

The tool can also convert character and variable definitions into Ren'Py readable format.

The tool handles only the most common use cases, and isn't meant to replace the actual
hard work needed to make the edge cases work.

## Table of contents
- [Flow conversion](#flow-conversion)
- [Character conversion](#character-conversion)
- [Variable conversion](#variable-conversion)

## Flow conversion

Current the tool assumes the following structure:
1. Main dialogue level named according to the labels. Target filenames are in text field.
2. Dialogue fragments have speakers with lines. Any scene commands etc. are assumed to be in "stage direction" portion of the dialogue frament.

## Character conversion

To get the characters to export correctly, you need to set up the structure in articy and/or
Python code to match each other first. The default setup assumes the following setup in articy
and Python:

### Python expectations
You have defined a Ren'py Character compatible class of your own that includes any and all
possible customizations and in addition forwards the calls to linked char. Example code:

``python

    class RenCharacter:
        def __init__(self, name, color, met_already=False, **kwargs):
            self.char = Character(name, color=color, **kwargs)
            self.met_already = met_already

        def __call__(self, *args, **kwargs):
            self.char.__call__(*args, **kwargs)
``

### Articy expectations

the CHARACTER_ENTITY 
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

Note you need to first create a new variable set under Global Variables in articy before 
you can add any variables.
![Creating namespace](./imgs/creating_namespace.png)
Image 1 - Creating namespace (variable set)

![Example of global variable definition.](./imgs/global_variables.png)
Image 2 - Example of global variable definition.
