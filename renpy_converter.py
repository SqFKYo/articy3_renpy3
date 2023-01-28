# -*- coding: utf-8 -*-

from collections import defaultdict, deque, namedtuple
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator, List

import networkx as nx

CHARACTER_CLASS = "RenCharacter"

Character = namedtuple("Character", "name color speaker")

Variable = namedtuple("Variable", "name_space name type value description")


class ParseableTypes:
    CHARACTER = "RenCharacter"
    DIALOGUE = "Dialogue"
    FRAGMENT = "DialogueFragment"
    INJECTED_FRAGMENT = "InjectedFragment"
    JUMP = "Jump"
    MENU_ITEM = "MenuItem"
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
    speaker_id: str
    text: str
    scene: str
    output_pins: List[str]
    speaker: str = ""

    def __repr__(self):
        returnable = ""
        if self.scene:
            returnable += f"    scene {self.scene}\n"
        returnable += f'    {self.speaker} "{self.text}"\n'
        return returnable


@dataclass
class InjectedFragment(Fragment):
    python_condition: str = ""
    python_outcome: str = ""

    def __repr__(self):
        returnable = super().__repr__()
        if self.python_outcome:
            returnable += f"    {self.python_outcome}\n"
        # If there's condition, we need to start from the previous line and put everything else within that block
        if self.python_condition:
            returnable = f"    {self.python_condition}:\n" + returnable.replace(" "*4, " "*8)
        return returnable

@dataclass
class Jump:
    obj_id: str
    parent: str
    target: str

    def __repr__(self):
        return "    jump {0}\n\n"

@dataclass
class Menu(Fragment):
    def __repr__(self):
        returnable = f"    menu:\n        "
        if self.speaker:
            returnable += f"{self.speaker} "
        returnable += f'"{self.text}"\n\n'
        return returnable


@dataclass
class MenuItem(InjectedFragment):
    ordinal: int = 0
    selected_text: str = ""

    def __repr__(self):
        returnable = f'        "{self.text}"'
        if self.python_condition:
            returnable += f" {self.python_condition}"
        returnable += ":\n"
        if self.python_outcome:
            returnable += f"            {self.python_outcome}\n"
        if self.selected_text:
            returnable += "            "
            if self.speaker:
                returnable += f"{self.speaker} "
            returnable += f'"{self.selected_text}"\n'
        return returnable


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
        self.ordinals.update(
            {f.obj_id: getattr(f, "ordinal", 0) for f in self._fragments}
        )

    def _initialize_speakers(self):
        for f in self._fragments:
            try:
                f.speaker = self.char_map[f.speaker_id]
            except AttributeError:
                # e.g. Jump
                pass

    @property
    def dialogues(self):
        return {diag.obj_id: diag for diag in self._dialogues}

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
                char_color = raw_char["Template"]["RenCharProps"][
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

        def parse_injected(obj) -> InjectedFragment:
            cond = obj["Template"]["PythonInjections"]["PythonCondition"]
            output = obj["Template"]["PythonInjections"]["PythonOutcome"]
            return InjectedFragment(
                *parse_basic_fragment(obj["Properties"]),
                python_condition=cond,
                python_outcome=output,
            )

        def parse_jump(props) -> Jump:
            return Jump(
                props["Id"],
                props["Parent"],
                props["Target"],
            )

        def parse_menu(props) -> Menu:
            return Menu(
                *parse_basic_fragment(props),
            )

        def parse_menu_item(obj) -> MenuItem:
            cond = obj["Template"]["PythonInjections"]["PythonCondition"]
            output = obj["Template"]["PythonInjections"]["PythonOutcome"]
            selected_text = obj["Template"]["MenuItem"]["OptionSelectedText"]
            ordinal = int(obj["Template"]["MenuItem"]["OrdinalNumber"])
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
                    case ParseableTypes.INJECTED_FRAGMENT:
                        self._fragments.append(parse_injected(obj))
                    case ParseableTypes.JUMP:
                        self._fragments.append(parse_jump(obj["Properties"]))
                    case ParseableTypes.MENU:
                        self._fragments.append(parse_menu(obj["Properties"]))
                    case ParseableTypes.MENU_ITEM:
                        self._fragments.append(parse_menu_item(obj))
                    case _:
                        pass
        self._initialize_charmap()
        self._initialize_ordinals()
        self._initialize_speakers()

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
                if dialogue.target_file != target_file:
                    continue
                f.write(f"label {dialogue.label}:\n")
                dumpable_frags = [
                    frag for frag in self._fragments if dialogue.obj_id == frag.parent
                ]
                sorted_frags = self.sort_elements(dumpable_frags)
                previous = None
                # Need to keep tabs on what was the last written, so we can check parent if needed
                for frag in sorted_frags:
                    try:
                        to_write = str(self.fragments[frag])
                        if to_write.startswith("    jump"):
                            # If we got here through Menu, we need way more indentation
                            to_write = to_write.format(self.dialogues[self.fragments[frag].target].label)
                            if isinstance(self.fragments[previous], MenuItem):
                                to_write = "        " + to_write
                        f.write(to_write)
                    except KeyError:
                        # Fragment leads its own parent (Dialogue to Dialogue connection) or new Dialogue
                        # Regular flowing dialogues case
                        try:
                            next_diag = self.dialogues[self.dialogues[frag].output_pins[0]]
                            f.write(f"\n    jump {next_diag.label}\n\n")
                        except IndexError:
                            # No output_pins, link to new Dialogue directly, only used with MenuItems
                            next_diag = self.dialogues[frag]
                            f.write(f"            jump {next_diag.label}\n\n")
                    finally:
                        previous = frag

    def sort_elements(self, sortable_elements: list) -> Iterator:
        """
        We're sorting a graph, so let's use NetworkX to create the graph
        We assume that more complex returning paths will be handled with jumps to other labels, so graph is acyclic.
        If there's no menu, there is no branching
        If there's menu, ordinal decides the order
        The choices either point to a jump or get all back to the same new Fragmentg files.
        """
        e_graph = nx.DiGraph()

        for e in sortable_elements:
            try:
                e_graph.add_edges_from(
                    [e.obj_id, output_pin] for output_pin in e.output_pins
                )
            except AttributeError:
                # Jumps don't have output_pins, but target
                e_graph.add_edges_from([(e.obj_id, e.target)])
        root = next(n for n in e_graph.nodes if not set(e_graph.predecessors(n)))

        d = deque([root])

        while d:
            next_out = d.popleft()

            try:
                # If this one is jump, we just return it without handling the child
                if isinstance(self.fragments[next_out], Jump):
                    next_is_jump = True
                else:
                    next_is_jump = False
            except KeyError:
                next_is_jump = False

            if not next_is_jump:
                raw_children = (n for n in e_graph.successors(next_out))
                # Branching back produces duplicates, need to not add the nodes already in deque
                children = [c for c in raw_children if c not in d]
                immediate_handling = False
                try:
                    immediate_handling = isinstance(self.fragments[children[0]], Jump)
                except KeyError:
                    # Is the child Dialogue that is not the parent?
                    if self.dialogues[children[0]] != self.dialogues[self.fragments[next_out].parent]:
                        immediate_handling = True
                except IndexError:
                    # No further targets
                    pass
                if immediate_handling:
                    d.appendleft(children[0])
                else:
                    d.extend(sorted((c for c in children), key=self.ordinals.get))

            yield next_out
