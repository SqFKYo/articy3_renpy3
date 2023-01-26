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
    And Fragment with obj_id of 0x01000000000002D4 has output_pins attribute 0x01000000000002A7
    Then we have Fragment with obj_id of 0x01000000000002A7
    And Fragment with obj_id of 0x01000000000002A7 has parent attribute 0x0100000000000286
    And Fragment with obj_id of 0x01000000000002A7 has speaker attribute maeve
    And Fragment with obj_id of 0x01000000000002A7 has text attribute Game will end now.
    And Fragment with obj_id of 0x01000000000002A7 has output_pins attribute <Empty list>

  Scenario: More complex structures are read correctly
    Then Fragment with obj_id of 0x010000000000045E has text attribute Do you want to have the chance to meet the characters multiple times?
    And Fragment with obj_id of 0x010000000000045E has speaker attribute maeve
    And Fragment with obj_id of 0x010000000000045E has output_pins attribute 0x01000000000004A3,0x01000000000004A9
    Then Fragment with obj_id of 0x01000000000004A9 has text attribute No
    And Fragment with obj_id of 0x01000000000004A9 has speaker attribute maeve
    And Fragment with obj_id of 0x01000000000004A9 has python_condition attribute <Empty>
    And Fragment with obj_id of 0x01000000000004A9 has python_outcome attribute $ flags.meet_again = False
    And Fragment with obj_id of 0x01000000000004A9 has selected_text attribute You have selected that you do not want to have the option to meet characters multiple times.
    And Fragment with obj_id of 0x01000000000004A9 has ordinal attribute 2
    Then Fragment with obj_id of 0x01000000000007C3 has speaker attribute <Empty>
    Then Fragment with obj_id of 0x01000000000007C3 has text attribute I think I want to have the option to meet the characters multiple times.
    And Fragment with obj_id of 0x01000000000007C3 has python_condition attribute if not flags.meet_again
    And Fragment with obj_id of 0x01000000000007C3 has python_outcome attribute $ flags.meet_again = True
    And Fragment with obj_id of 0x01000000000007C3 has ordinal attribute 1
    And Fragment with obj_id of 0x0100000000000950 has text attribute Hey, I'm Maeve, this game's MC!
    And Fragment with obj_id of 0x0100000000000950 has scene attribute meet_maeve
    And Fragment with obj_id of 0x0100000000000950 has python_condition attribute <Empty>
    And Fragment with obj_id of 0x0100000000000950 has python_outcome attribute $ maeve.met_already = True
