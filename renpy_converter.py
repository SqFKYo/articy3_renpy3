# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple, deque
from dataclasses import dataclass, field
from functools import total_ordering
import json
from pathlib import Path
from typing import List, TextIO

CHARACTER_CLASS = "RenCharacter"

Character = namedtuple("Character", "name color speaker")

Variable = namedtuple("Variable", "name_space name type value description")


class ParseableTypes:
    CHARACTER = "Ren_py_character"
    DIALOGUE = "Dialogue"
    FRAGMENT = "DialogueFragment"

@dataclass
class Dialogue:
    obj_id: str
    label: str
    target_file: str
    output_pins: list[str]

@total_ordering
@dataclass
class Fragment:
    obj_id: str
    parent: str
    speaker: str
    text: str
    stage_directions: str
    output_pins: List[str]

    def __eq__(self, other):
        return self.obj_id == other.obj_id

    def __lt__(self, other):
        return self.obj_id in other.output_pins

class Converter:
    def __init__(self, input_file: Path) -> None:
        self._characters = []
        self._dialogues = []
        self._fragments = []
        self._input_file = input_file
        self._variables = []

    def read_input(self) -> None:
        def get_outputs(pins: list) -> list:
            try:
                output_pins = [x["Target"] for x in pins[0]["Connections"]]
            except KeyError:
                output_pins = []
            return output_pins

        def parse_char(raw_char) -> Character:
            char_name = raw_char["Properties"]["DisplayName"]
            char_speaker = raw_char["Properties"]["Id"]
            try:
                char_color = raw_char["Template"]["Ren_py_character_properties"][
                    "Color"
                ]
            except IndexError:
                # No color defined, defaulting to black
                char_color = "000000"
            return Character(char_name, char_color, char_speaker)

        def parse_dialogue(props) -> Dialogue:
            return Dialogue(
                props["Id"],
                props["DisplayName"],
                props["Text"],
                get_outputs(props["OutputPins"]),
            )

        def parse_fragment(props) -> Fragment:
            return Fragment(
                props["Id"],
                props["Parent"],
                props["Speaker"],
                props["Text"],
                props["StageDirections"],
                get_outputs(props["OutputPins"]),
            )

        def parse_var(raw_var, name_space) -> Variable:
            return Variable(
                name_space,
                raw_var["Variable"],
                raw_var["Type"],
                raw_var["Value"],
                raw_var["Description"],
            )

        with open(self._input_file, "r") as f:
            dump = json.load(f)
            name_spaces = dump["GlobalVariables"]
            for name_space in name_spaces:
                self._variables.extend(
                    [
                        parse_var(v, name_space=name_space["Namespace"])
                        for v in name_space["Variables"]
                    ]
                )
            for obj in dump["Packages"][0]["Models"]:
                match obj["Type"]:
                    case ParseableTypes.CHARACTER:
                        self._characters.append(parse_char(obj))
                    case ParseableTypes.DIALOGUE:
                        self._dialogues.append(parse_dialogue(obj["Properties"]))
                    case ParseableTypes.FRAGMENT:
                        self._fragments.append(parse_fragment(obj["Properties"]))
                    case _:
                        pass

    def write_init_rpy(self, file_type: str, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            if file_type.lower() == "character":
                f.write(
                    "# Declarations for game characters and their important values\n\n"
                )
                for c in self._characters:
                    f.write(
                        f'define {c.name.lower()} = {CHARACTER_CLASS}("{c.name}", color="{c.color}")\n'
                    )
            elif file_type.lower() == "variable":
                f.write("# Declarations of global variables\n\n")
                for v in self._variables:
                    f.write(f"default {v.name_space}.{v.name} = {v.value}\n")
            else:
                raise NotImplementedError("Unknown init rpy write request")

    def write_scene_rpy(self, target_file: str, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            for dialogue in self._dialogues:
                first = True
                if dialogue.target_file == target_file:
                    if first:
                        first = False
                    else:
                        f.write('\n\n')
                    f.write(f"{dialogue.label}:\n")
                    for frag in sorted((frag for frag in self._fragments if dialogue.obj_id == frag.parent), reverse=True):
                        f.write(f'\t{frag.speaker} "{frag.text}"\n')


"""
@dataclass
class Label:
    target_file: str
    label_name: str
    obj_id: str
    links: list[str]
    fragments: list[DialogueFragment] = field(default_factory=list)

    def __iter__(self) -> Iterator[DialogueFragment]:
        return iter(self.fragments)


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

    def form_label(raw_dialogue: dict) -> Label:
        # Forming labels first to get the higher order connections done
        props = raw_dialogue["Properties"]
        links = get_links(props["OutputPins"])
        return Label(props["Text"], props["DisplayName"], props["Id"], links)

    labels = {d["Properties"]["Id"]: form_label(d) for d in raw_dialogues}

    def form_frag(raw_fragment: dict) -> DialogueFragment:
        # Forming DialogueFraments to put together the actual scenario
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

    def sort_by_links(
        linked_objs: List[Union[Label, DialogueFragment]]
    ) -> List[Union[Label, DialogueFragment]]:
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
"""
