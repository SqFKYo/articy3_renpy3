Feature: Reading all the different Fragments in

  Background:
    Given Input json file is .\test_files\articy3_renpy3_tests.json
    When Converter is created
    And Input file is read in

  Scenario: Basic fragments are read in correctly
    Then we have Fragment with obj_id of 0x01000000000002D4
    And Fragment with obj_id of 0x01000000000002D4 has parent attribute 0x0100000000000286
    And Fragment with obj_id of 0x01000000000002D4 has speaker attribute faye
    And Fragment with obj_id of 0x01000000000002D4 has text attribute We hope you'll see us soon!
    And Fragment with obj_id of 0x01000000000002D4 has output_pins attribute leading to 0x01000000000002A7,
    Then we have Fragment with obj_id of 0x01000000000002A7
    And Fragment with obj_id of 0x01000000000002A7 has parent attribute 0x0100000000000286
    And Fragment with obj_id of 0x01000000000002A7 has speaker attribute maeve
    And Fragment with obj_id of 0x01000000000002A7 has text attribute Game will end now.
    And Fragment with obj_id of 0x01000000000002A7 has output_pins attribute leading to ,

    """
    obj_id: str
    parent: str
    speaker: str
    text: str
    stage_directions: str
    output_pins: List[str]
    """