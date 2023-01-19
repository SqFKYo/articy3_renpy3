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
    if attr == 'speaker':
        try:
            to_test = context.converter.char_map[to_test]
        except KeyError:
            to_test = None
    elif attr == 'output_pins':
        target_value = target_value.split(',')
    assert to_test == target_value
