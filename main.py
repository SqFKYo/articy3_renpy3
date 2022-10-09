# -*- coding: utf-8 -*-

from pathlib import Path

TEST_JSON = Path(r"C:\Users\sqfky\Desktop\Communing with Faye.json")


def convert_characters(chars_json: dict, target_file: Path = None) -> None:
    ...


def convert_fragments(fragments_json: dict, target_file: Path = None) -> None:
    ...


def fetch_parts(file: Path) -> (dict, dict):
    ...


def main(json_file):
    chars, fragments = fetch_parts(file=json_file)
    convert_characters(chars)
    convert_fragments(fragments)


if __name__ == "__main__":
    main(json_file=TEST_JSON)
