Feature: Testing writing the character definitions

  Scenario: We should have two RenCharacters defined
    Given Input json file is .\test_files\articy3_renpy3_tests.json
    When Converter is created
    And Input file is read in
    And Character file is written to .\test_files\output_folder\characters.rpy
    Then Written character file is equal to .\test_files\characters.rpy
