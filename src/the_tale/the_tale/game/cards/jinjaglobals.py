
from dext.common.utils import jinja2

from the_tale.game.cards import logic


@jinja2.jinjaglobal
def receive_cards_url():
    return jinja2.Markup(logic.receive_cards_url())


@jinja2.jinjaglobal
def combine_cards_url():
    return jinja2.Markup(logic.combine_cards_url())


@jinja2.jinjaglobal
def move_to_storage_url():
    return jinja2.Markup(logic.move_to_storage_url())


@jinja2.jinjaglobal
def move_to_hand_url():
    return jinja2.Markup(logic.move_to_hand_url())


@jinja2.jinjaglobal
def use_card_url(card_uid):
    return jinja2.Markup(logic.use_card_url(card_uid))


@jinja2.jinjaglobal
def get_cards_url():
    return jinja2.Markup(logic.get_cards_url())


@jinja2.jinjaglobal
def transform_cards_url():
    return jinja2.Markup(logic.transform_cards_url())
