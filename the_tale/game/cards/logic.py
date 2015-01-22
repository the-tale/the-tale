# coding: utf-8


from the_tale.game.cards import effects


def create_card(type, available_for_auction):
    return effects.EFFECTS[type].create_card(available_for_auction=available_for_auction)
