label game_end:
    maeve "We are at the end of the demonstration."
    if maeve.met_already and not faye.met_already:
        maeve "Yay, you met me! Next time, you should check out Faye too."
    elif faye.met_already and not maeve.met_already:
        faye "Yay, you met me! Next time, you should check out Maeve too."
    elif maeve.met_already and faye.met_already:
        maeve "Cool, you met both girls!"
    else:
        "Huh, you didn't meet anyone? What's the point?"
    faye "We hope you'll see us soon!"
    maeve "Game will end now."
