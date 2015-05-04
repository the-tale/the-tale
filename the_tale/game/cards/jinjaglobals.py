# coding: utf-8

from dext.common.utils import jinja2

from the_tale.game.cards import logic


@jinja2.jinjaglobal
def get_card_url():
    return jinja2.Markup(logic.get_card_url())


@jinja2.jinjaglobal
def combine_cards_url(cards_uids=None):
    return jinja2.Markup(logic.combine_cards_url(cards_uids))


@jinja2.jinjaglobal
def use_card_url(card_uid):
    return jinja2.Markup(logic.use_card_url(card_uid))
