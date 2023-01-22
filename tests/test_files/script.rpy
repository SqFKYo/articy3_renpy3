label start:
    maeve "This is a short test run for the game's integration testing."

    menu: 
        maeve "Do you want to have the chance to meet the characters multiple times?"

        "Yes":
            $ flags.meet_again = True
            maeve "You have selected that you want to have the option to meet characters multiple times."

        "No":
            $ flags.meet_again = False
            maeve "You have selected that you do not want to have the option to meet characters multiple times."

    menu:
        maeve "Would you like to change your choice?"

        "I think I want to have the option to meet the characters multiple times." if not flags.meet_again:
            $ flags.meet_again = True

        "I don't think I want to meet the character multiple times after all." if flags.meet_again:
            $ flags.meet_again = False

        "No I'm happy with my choice.":
            $ ...

    faye "Testing will commence now."

    jump meet_select
