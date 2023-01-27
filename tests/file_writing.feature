Feature: Writing the character definitions

  Background:
    Given Input json file is .\test_files\articy3_renpy3_tests.json
    When Converter is created
    And Input file is read in

  Scenario: We should have two RenCharacters defined
    When Character file is written to .\output_folder\characters.rpy
    Then Written file is equal to .\test_files\characters.rpy

  Scenario: We should have one variable defined
    When Variable file is written to .\output_folder\variables.rpy
    Then Written file is equal to .\test_files\variables.rpy

  Scenario: Simple scene file with one label
    When Scene file scene2.rpy is written to .\output_folder\scene2.rpy
    Then Written file is equal to .\test_files\scene2.rpy

  Scenario: More complex scene with single label encapsulating multiple choices and variable changes
    When Scene file script.rpy is written to .\output_folder\script.rpy
    Then Written file is equal to .\test_files\script.rpy
