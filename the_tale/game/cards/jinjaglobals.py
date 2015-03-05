# coding: utf-8

import jinja2

from dext.jinja2.decorators import jinjaglobal

from the_tale.game.cards import logic


@jinjaglobal
def get_card_url():
    return jinja2.Markup(logic.get_card_url())


@jinjaglobal
def combine_cards_url(cards_uids=None):
    return jinja2.Markup(logic.combine_cards_url(cards_uids))


@jinjaglobal
def use_card_url(card_uid):
    return jinja2.Markup(logic.use_card_url(card_uid))
