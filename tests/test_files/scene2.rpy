label game_end:
    maeve "We are at the end of the demonstration."
    if not flags.meet_again:
        maeve "It seems you didn't want to meet the characters again. Maybe next time?"
    if flags.meet_again:
        maeve "You really enjoyed yourself and wanted to meet the character over an over again. Great!"
    faye "We hope you'll see us soon!"
    maeve "Game will end now."
