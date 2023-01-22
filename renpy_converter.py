# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator, List

import networkx as nx

CHARACTER_CLASS = "RenCharacter"

Character = namedtuple("Character", "name color speaker")

Variable = namedtuple("Variable", "name_space name type value description")


class ParseableTypes:
    CHARACTER = "Ren_py_character"
    DIALOGUE = "Dialogue"
    FRAGMENT = "DialogueFragment"
    MENU_ITEM = "Menu_option"
    MENU = "Menu"

@dataclass
class Dialogue:
    obj_id: str
    label: str
    target_file: str
    output_pins: list[str]

@dataclass
class Fragment:
    obj_id: str
    parent: str
    speaker: str
    text: str
    stage_directions: str
    output_pins: List[str]
    menu: bool
    python_condition: str
    python_outcome: str
    selected_text: str


class Converter:
    def __init__(self, input_file: Path) -> None:
        self._characters = []
        self._dialogues = []
        self._fragments = []
        self._input_file = input_file
        self._variables = []
        self.char_map = defaultdict(str)

    def _initialize_charmap(self):
        self.char_map.update({char.speaker: char.name.lower() for char in self._characters})

    @property
    def fragments(self):
        return {frag.obj_id: frag for frag in self._fragments}

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

        def parse_basic_fragment(props) -> List:
            return [
                props["Id"],
                props["Parent"],
                props["Speaker"],
                props["Text"],
                props["StageDirections"],
                get_outputs(props["OutputPins"]),
            ]
        def parse_fragment(props) -> Fragment:
            return Fragment(
                *parse_basic_fragment(props),
                menu=False,
                python_condition="",
                python_outcome="",
                selected_text="",
            )

        def parse_menu(props) -> Fragment:
            return Fragment(
                *parse_basic_fragment(props),
                menu=True,
                python_condition="",
                python_outcome="",
                selected_text="",
            )

        def parse_menu_item(obj) -> Fragment:
            cond = obj["Template"]["Menu_option"]["python_condition"]
            output = obj["Template"]["Menu_option"]["python_outcome"]
            selected_text = obj["Template"]["Menu_option"]["option_selected_text"]
            return Fragment(
                *parse_basic_fragment(obj["Properties"]),
                menu=False,
                python_condition=cond,
                python_outcome=output,
                selected_text=selected_text,
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
                    case ParseableTypes.MENU:
                        self._fragments.append(parse_menu(obj["Properties"]))
                    case ParseableTypes.MENU_ITEM:
                        self._fragments.append(parse_menu_item(obj))
                    case _:
                        pass
        self._initialize_charmap()

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
                if dialogue.target_file == target_file:
                    f.write(f"{dialogue.label}:\n")
                    dumpable_frags = [frag for frag in self._fragments if dialogue.obj_id == frag.parent]
                    sorted_frags = sort_elements(dumpable_frags)
                    for frag in sorted_frags:
                        f.write(f'    {self.char_map[self.fragments[frag].speaker]} "{self.fragments[frag].text}"\n')

def sort_elements(sortable_elements: list) -> Iterator:
    # We're sorting a graph, so let's use NetworkX
    # We assume that more complex returning paths will be handled with jumps to other labels, so graph is acyclic.
    e_graph = nx.DiGraph()
    for e in sortable_elements:
        e_graph.add_edges_from([e.obj_id, output_pin] for output_pin in e.output_pins)
    return nx.lexicographical_topological_sort(e_graph, key=None)

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
