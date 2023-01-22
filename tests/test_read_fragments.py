# -*- coding: utf-8 -*-
from pytest_bdd import parsers, scenarios, then

scenarios("fragment_reading.feature")


@then(parsers.parse("we have Fragment with obj_id of {obj_id}"))
def assert_fragment_exists(context, obj_id):
    assert obj_id in context.converter.fragments


@then(
    parsers.parse(
        "Fragment with obj_id of {obj_id} has {attr} attribute {target_value}"
    )
)
def assert_frag_attr_value(context, obj_id, attr, target_value):
    to_test = getattr(context.converter.fragments[obj_id], attr)
    if target_value == "<Empty>":
        target_value = ""
    elif target_value == "<Empty list>":
        target_value = []
    if attr == 'speaker':
        to_test = context.converter.char_map[to_test]
    elif attr == 'output_pins':
        try:
            target_value = target_value.split(',')
        except AttributeError:
            # None trying to get split
            pass
    elif attr == 'ordinal':
        target_value = int(target_value)
    assert to_test == target_value
