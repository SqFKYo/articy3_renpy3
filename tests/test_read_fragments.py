# -*- coding: utf-8 -*-
from pytest_bdd import parsers, scenarios, then

scenarios("fragment_reading.feature")

@then(parsers.parse("we have Fragment with obj_id of {obj_id}"))
def assert_fragment_exists(context, obj_id):
    assert obj_id in context.converter.fragments
