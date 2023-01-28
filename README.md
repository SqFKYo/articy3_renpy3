# articy3_renpy3
articy:draft 3 to Ren'Py 3 converter

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
