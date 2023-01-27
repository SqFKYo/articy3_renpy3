Feature: Writing file with branching and a jump

  Background:
    Given Input json file is .\test_files\articy3_renpy3_tests.json
    When Converter is created
    And Input file is read in

  Scenario: More complex scene with single label encapsulating multiple choices, variable changes and a jump
    When Scene file script.rpy is written to .\output_folder\script.rpy
    Then Written file is equal to .\test_files\script.rpy
