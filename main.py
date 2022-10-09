# -*- coding: utf-8 -*-

from collections import namedtuple
import json
from pathlib import Path

CHARACTER_ENTITY = "Ren_py_character"
TEST_JSON = Path(r"C:\Users\sqfky\Desktop\Communing with Faye.json")

Character = namedtuple("Charater", "name color")


def convert_characters(raw_chars: list, target_file: Path = None) -> None:
    if target_file is None:
        target_file = Path(r".\characters.rpy")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write("# Declarations for game characters and their important values\n\n")
        for raw_char in raw_chars:
            char = process_char(raw_char)
            f.write(
                f'define {char.name.lower()} = Character("{char.name}", color="{char.color}")\n'
            )


def convert_flow(raw_fragments: list, target_file: Path = None) -> None:
    ...


def fetch_parts(file: Path) -> (list, list):
    with open(file, "r") as f:
        dump = json.load(f)
        chars = [
            c for c in dump["Packages"][0]["Models"] if c["Type"] == CHARACTER_ENTITY
        ]

    return chars, []


def process_char(raw_char: dict) -> Character:
    char_name = raw_char["Properties"]["DisplayName"]
    try:
        char_color = raw_char["Template"]["Ren_py_character_properties"]["Color"]
    except IndexError:
        # No color defined, defaulting to black
        char_color = "000000"
    return Character(char_name, char_color)


def main(json_file):
    raw_chars, raw_fragments = fetch_parts(file=json_file)
    convert_characters(raw_chars)
    convert_flow(raw_fragments)


if __name__ == "__main__":
    main(json_file=TEST_JSON)
