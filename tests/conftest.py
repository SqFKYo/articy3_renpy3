# -*- coding: utf-8 -*-

from pathlib import Path

from pytest import fixture
from pytest_bdd import given, parsers, then, when

from renpy_converter import Converter


@fixture
def context():
    class Context:
        def __init__(self):
            pass

    return Context()


@given(parsers.parse("Input json file is {input_path}"))
def define_input_path(context, input_path):
    context.input_path = Path(input_path).resolve()


@when("Converter is created")
def create_converter(context):
    context.converter = Converter(input_file=context.input_path)


@when("Input file is read in")
def read_input_file(context):
    context.converter.read_input()


@when(parsers.parse("{file_type} file is written to {output_path}"))
def write_init_file(context, file_type, output_path):
    output_path = Path(output_path).resolve()
    context.output_path = output_path  # For later testing
    context.converter.write_init_rpy(file_type, output_path)


@when(parsers.parse("Scene file {scene_name} is written to {output_path}"))
def write_scene_file(context, scene_name, output_path):
    output_path = Path(output_path).resolve()
    context.output_path = output_path
    context.converter.write_scene_rpy(scene_name, output_path)


@then(parsers.parse("Written file is equal to {target_file}"))
def assert_written_file_equals(context, target_file):
    with open(context.output_path, "r") as written, open(target_file, "r") as target:
        assert written.read() == target.read()
