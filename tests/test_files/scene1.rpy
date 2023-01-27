label meet_select:
    menu:
        "Who would you like to meet?"

        "Maeve" if flags.meet_again or not maeve.met_already:
            jump meet_maeve

        "Faye" if flags.meet_again or not faye.met_already:
            jump meet_faye

        "I'm done with meeting characters.":
            "Meeting testing is over, let's wrap this up!"

    jump game_end

label meet_maeve:
    scene meet_maeve
    maeve "Hey, I'm Maeve, this game's MC!"
    $ maeve.met_already = True
    jump meet_select

label meet_faye:
    scene meet_faye
    faye "Hey I'm Faye, the main LI of this game."
    $ faye.met_already = True
    jump meet_select

