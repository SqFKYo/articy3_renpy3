# articy3_renpy3
articy:draft 3 to Ren'Py 3 converter

## Flow conversion

Current the tool assumes the following structure:
1. Main dialogue level named according to the target filenames.
2. First sublevel of dialogues corresponding to labels
3. Dialogue fragments corresponding to texts

Any scene commands etc. are assumed to be in "stage direction" 
portion of the dialogue frament.



## Character conversion

To get the characters to export correctly, you need to set the CHARACTER_ENTITY 
to match the value of the Ren'Py character entity you've created in articy.
My default technical name is "Ren_py_character".

If you want the converter to support color for the character, the current
code assumes the Ren'Py character has Template named 
"Ren_py_character_properties", which then has field named "Color".
