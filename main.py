# -*- coding: utf-8 -*-

from collections import namedtuple
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import List

CHARACTER_ENTITY = "Ren_py_character"
TEST_JSON = Path(r"C:\Users\sqfky\Desktop\Communing with Faye.json")

Character = namedtuple("Character", "name color speaker")
DialogueFragment = namedtuple(
    "DialogueFragment", "speaker scene_direction diag_id prev_id next_id"
)

@dataclass
class Label:
    target_file: str
    label_name: str
    label_id: str
    links: list[str]
    fragments: list[DialogueFragment] = field(default_factory=list)

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


def convert_flow(raw_dialogues: list, raw_fragments: list, chars, target_folder: Path = None) -> None:
    # Find the Dialogues to form the labels and connections between them
    def form_label(raw_dialogue: dict) -> Label:
        props = raw_dialogue["Properties"]
        try:
            links = [link["Connections"][0]["Target"] for link in props["OutputPins"]]
        except KeyError:
            links = []
        return Label(props["Text"], props["DisplayName"], props["Id"], links)

    labels = [
        form_label(d) for d in raw_dialogues
    ]

    # Find the DialogueFraments to find the actual text
    pass


def fetch_parts(file: Path) -> (list, list, list):
    with open(file, "r") as f:
        dump = json.load(f)
        chars = [
            c for c in dump["Packages"][0]["Models"] if c["Type"] == CHARACTER_ENTITY
        ]
        dialogues = [d for d in dump["Packages"][0]["Models"] if d["Type"] == "Dialogue"]
        diag_fragments = [d for d in dump["Packages"][0]["Models"] if d["Type"] == "DialogueFragment"]

    return chars, dialogues, diag_fragments


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
    raw_chars, raw_dialogues, raw_fragments = fetch_parts(file=json_file)
    chars = convert_characters(raw_chars)
    convert_flow(raw_dialogues, raw_fragments, chars)


if __name__ == "__main__":
    main(json_file=TEST_JSON)
