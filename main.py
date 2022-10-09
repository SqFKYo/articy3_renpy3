# -*- coding: utf-8 -*-

from collections import namedtuple
import json
from pathlib import Path
from typing import List

CHARACTER_ENTITY = "Ren_py_character"
DIALOGUES = ["Dialogue", "DialogueFrament"]
TEST_JSON = Path(r"C:\Users\sqfky\Desktop\Communing with Faye.json")

Character = namedtuple("Charater", "name color speaker")


def convert_characters(raw_chars: list, target_file: Path = None) -> List[Character]:
    if target_file is None:
        target_file = Path(r".\characters.rpy")
    chars = [process_char(raw_char) for raw_char in raw_chars]
    with open(target_file, "w", encoding="utf-8") as f:
        f.write("# Declarations for game characters and their important values\n\n")
        for char in chars:
            f.write(
                f'define {char.name.lower()} = Character("{char.name}", color="{char.color}")\n'
            )
    return chars


def convert_flow(raw_dialogues: list, chars, target_file: Path = None) -> None:
    # Fetch the Dialogues with .rpy DisplayName to find our filenames
    pass
    # target_files = [TargetFile(file_name, file_id) ]

    # Find the Dialogues without .rpy DisplayName to find the labels
    pass

    # Find the DialogueFraments to find the actual text
    pass


def fetch_parts(file: Path) -> (list, list):
    with open(file, "r") as f:
        dump = json.load(f)
        chars = [
            c for c in dump["Packages"][0]["Models"] if c["Type"] == CHARACTER_ENTITY
        ]
        dialogues = [
            d for d in dump["Packages"][0]["Models"] if d["Type"] in DIALOGUES
        ]

    return chars, dialogues


def process_char(raw_char: dict) -> Character:
    char_name = raw_char["Properties"]["DisplayName"]
    char_speaker = raw_char["Properties"]["Id"]
    try:
        char_color = raw_char["Template"]["Ren_py_character_properties"]["Color"]
    except IndexError:
        # No color defined, defaulting to black
        char_color = "000000"
    return Character(char_name, char_color, char_speaker)


def main(json_file):
    raw_chars, raw_dialogues = fetch_parts(file=json_file)
    chars = convert_characters(raw_chars)
    convert_flow(raw_dialogues, chars)


if __name__ == "__main__":
    main(json_file=TEST_JSON)
