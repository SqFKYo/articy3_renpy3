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
    And Fragment with obj_id of 0x01000000000002A7 has output_pins attribute <None>

  Scenario: Menu elements and injections are read correctly
    Then Fragment with obj_id of 0x010000000000045E has text attribute Do you want to have the chance to meet the characters multiple times?
    And Fragment with obj_id of 0x0100000000000905 has speaker attribute maeve
    And Fragment with obj_id of 0x0100000000000905 has output_pins attribute 0x01000000000004A3,0x01000000000004A9
    Then Fragment with obj_id of 0x01000000000004A9 has text attribute No
    And Fragment with obj_id of 0x01000000000004A9 has speaker attribute <None>
    And Fragment with obj_id of 0x01000000000004A9 has python_condition attribute <None>
    And Fragment with obj_id of 0x01000000000004A9 has python_outcome attribute $ flags.meet_again = False
    Then Fragment with obj_id of 0x01000000000007C3 has text attribute I think I want to have the option to meet the characters multiple times.
    And Fragment with obj_id of 0x01000000000007C3 has python_condition attribute $ flags.meet_again = False
    And Fragment with obj_id of 0x01000000000007C3 has python_outcome attribute $ flags.meet_again = True
