# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple, deque
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Iterator, List, Union

CHARACTER_ENTITY = "Ren_py_character"
TEST_JSON = Path(r"C:\Users\sqfky\Desktop\Communing with Faye.json")

Character = namedtuple("Character", "name color speaker")
DialogueFragment = namedtuple(
    "DialogueFragment", "speaker text stage_directions obj_id links"
)


@dataclass
class Label:
    target_file: str
    label_name: str
    obj_id: str
    links: list[str]
    fragments: list[DialogueFragment] = field(default_factory=list)

    def __iter__(self) -> Iterator[DialogueFragment]:
        return iter(self.fragments)


def convert_characters(
    raw_chars: list[dict], target_file: Path = None
) -> dict[str:str]:
    def process_char(raw_char: dict) -> Character:
        char_name = raw_char["Properties"]["DisplayName"]
        char_speaker = raw_char["Properties"]["Id"]
        try:
            char_color = raw_char["Template"]["Ren_py_character_properties"]["Color"]
        except IndexError:
            # No color defined, defaulting to black
            char_color = "000000"
        return Character(char_name, char_color, char_speaker)

    if target_file is None:
        target_file = Path(r".\characters.rpy")
    chars = [process_char(raw_char) for raw_char in raw_chars]
    with open(target_file, "w", encoding="utf-8") as f:
        f.write("# Declarations for game characters and their important values\n\n")
        for char in chars:
            f.write(
                f'define {char.name.lower()} = Character("{char.name}", color="{char.color}")\n'
            )
    return {char.speaker: char.name for char in chars}


def convert_flow(
    raw_dialogues: list[dict],
    raw_fragments: list[dict],
    chars: dict[str:str],
    target_folder: Path = None,
) -> None:
    def get_links(pin_list: list[dict]) -> list[str]:
        try:
            return [link["Connections"][0]["Target"] for link in pin_list]
        except KeyError:
            return []

    # Forming labels first to get the higher order connections done
    def form_label(raw_dialogue: dict) -> Label:
        props = raw_dialogue["Properties"]
        links = get_links(props["OutputPins"])
        return Label(props["Text"], props["DisplayName"], props["Id"], links)

    labels = {d["Properties"]["Id"]: form_label(d) for d in raw_dialogues}

    # Forming DialogueFraments to put together the actual scenario
    def form_frag(raw_fragment: dict) -> DialogueFragment:
        props = raw_fragment["Properties"]
        return DialogueFragment(
            props["Speaker"],
            props["Text"],
            props["StageDirections"],
            props["Id"],
            get_links(props["OutputPins"]),
        )

    # Add DialogueFragments to correct Dialogues
    for raw_fragment in raw_fragments:
        labels[raw_fragment["Properties"]["Parent"]].fragments.append(
            form_frag(raw_fragment)
        )

    # Sort Dialogues by output files
    label_files = defaultdict(list)
    for label in labels.values():
        label_files[label.target_file].append(label)

    def sort_by_links(linked_objs: List[Union[Label, DialogueFragment]]) -> List[Union[Label, DialogueFragment]]:
        # If length is under 2, no sorting is needed
        if len(linked_objs) < 2:
            return linked_objs
        # Assumes all the objects are linked with a single link to form a queue
        sorted_queue = deque([linked_objs.pop()])
        # Let's find previous and next objects for the queue we already have
        while len(linked_objs) > 0:
            first = sorted_queue[0]
            last = sorted_queue[-1]
            for possible in linked_objs:
                if first.obj_id in possible.links:
                    sorted_queue.appendleft(possible)
                    linked_objs.remove(possible)
                    break
                elif possible.obj_id in last.links:
                    sorted_queue.append(possible)
                    linked_objs.remove(possible)
                    break
        return list(sorted_queue)

    if target_folder is None:
        target_folder = Path(".")
    for file, writable_labels in label_files.items():
        with open(target_folder.joinpath(file), "w", encoding="utf-8") as f:
            for i, label in enumerate(sort_by_links(writable_labels)):
                if i > 0:
                    # Extra spacing between the labels
                    f.write("\n")
                f.write(f"label {label.label_name}:\n")
                for fragment in sort_by_links(label.fragments):
                    if fragment.stage_directions:
                        f.write(f"    {fragment.stage_directions}\n")
                    f.write(
                        f'    {chars[fragment.speaker].lower()} "{fragment.text}"\n'
                    )
                try:
                    f.write(f"    jump {labels[label.links[0]].label_name}\n")
                except IndexError:
                    # Last fragment of the story
                    pass


def fetch_parts(file: Path) -> (list, list, list):
    with open(file, "r") as f:
        dump = json.load(f)
        chars = [
            c for c in dump["Packages"][0]["Models"] if c["Type"] == CHARACTER_ENTITY
        ]
        dialogues = [
            d for d in dump["Packages"][0]["Models"] if d["Type"] == "Dialogue"
        ]
        diag_fragments = [
            d for d in dump["Packages"][0]["Models"] if d["Type"] == "DialogueFragment"
        ]

    return chars, dialogues, diag_fragments


def main(json_file):
    raw_chars, raw_dialogues, raw_fragments = fetch_parts(file=json_file)
    chars = convert_characters(raw_chars)
    convert_flow(raw_dialogues, raw_fragments, chars)


if __name__ == "__main__":
    main(json_file=TEST_JSON)
