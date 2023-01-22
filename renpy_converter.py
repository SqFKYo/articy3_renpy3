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


@dataclass
class Menu(Fragment):
    menu: bool = True


@dataclass
class MenuItem(Fragment):
    ordinal: int
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
        self.ordinals = defaultdict(int)

    def _initialize_charmap(self):
        self.char_map.update(
            {char.speaker: char.name.lower() for char in self._characters}
        )

    def _initialize_ordinals(self):
        self.ordinals.update({f.obj_id: getattr(f, 'ordinal', 0) for f in self._fragments})

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
            )

        def parse_menu(props) -> Menu:
            return Menu(
                *parse_basic_fragment(props),
            )

        def parse_menu_item(obj) -> MenuItem:
            cond = obj["Template"]["Menu_option"]["python_condition"]
            output = obj["Template"]["Menu_option"]["python_outcome"]
            selected_text = obj["Template"]["Menu_option"]["option_selected_text"]
            ordinal = int(obj["Template"]["Menu_option"]["ordinal_number"])
            return MenuItem(
                *parse_basic_fragment(obj["Properties"]),
                ordinal=ordinal,
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
        self._initialize_ordinals()

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
                    dumpable_frags = [
                        frag
                        for frag in self._fragments
                        if dialogue.obj_id == frag.parent
                    ]
                    sorted_frags = self.sort_elements(dumpable_frags)
                    for frag in sorted_frags:
                        f.write(
                            f'    {self.char_map[self.fragments[frag].speaker]} "{self.fragments[frag].text}"\n'
                        )


    def sort_elements(self, sortable_elements: list) -> Iterator:
        # We're sorting a graph, so let's use NetworkX
        # We assume that more complex returning paths will be handled with jumps to other labels, so graph is acyclic.
        # key helps to sort e.g. menu items in a way that we get constant results when writing files.
        e_graph = nx.DiGraph()

        for e in sortable_elements:
            e_graph.add_edges_from([e.obj_id, output_pin] for output_pin in e.output_pins)
        return nx.lexicographical_topological_sort(e_graph, key=self.ordinals.get)
