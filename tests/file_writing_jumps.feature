Feature: Writing file with multiple jumps and labels

  Scenario: More complex scene with multiple labels and possible infinite loop
    When Scene file scene1.rpy is written to .\output_folder\scene1.rpy
    Then Written file is equal to .\test_files\scene1.rpy
