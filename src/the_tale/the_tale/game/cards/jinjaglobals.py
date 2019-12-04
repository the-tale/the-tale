
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def receive_cards_url():
    return utils_jinja2.Markup(logic.receive_cards_url())


@utils_jinja2.jinjaglobal
def combine_cards_url():
    return utils_jinja2.Markup(logic.combine_cards_url())


@utils_jinja2.jinjaglobal
def move_to_storage_url():
    return utils_jinja2.Markup(logic.move_to_storage_url())


@utils_jinja2.jinjaglobal
def move_to_hand_url():
    return utils_jinja2.Markup(logic.move_to_hand_url())


@utils_jinja2.jinjaglobal
def use_card_url(card_uid):
    return utils_jinja2.Markup(logic.use_card_url(card_uid))


@utils_jinja2.jinjaglobal
def get_cards_url():
    return utils_jinja2.Markup(logic.get_cards_url())


@utils_jinja2.jinjaglobal
def transform_cards_url():
    return utils_jinja2.Markup(logic.transform_cards_url())
