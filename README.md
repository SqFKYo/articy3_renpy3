# articy3_renpy3
articy:draft 3 to Ren'Py 3 converter

To get the characters to export correctly, you need to set the CHARACTER_ENTITY 
to match the value of the Ren'Py character entity you've created in articy.
My default technical name is "Ren_py_character".

If you want the converter to support color for the character, the current
code assumes the Ren'Py character has Template named 
"Ren_py_character_properties", which then has field named "Color".
