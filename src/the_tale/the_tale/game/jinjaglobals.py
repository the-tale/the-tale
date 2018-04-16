
from dext.common.utils import jinja2

from the_tale.game import logic
from the_tale.game import turn


@jinja2.jinjaglobal
def game_info_url(account=None, client_turns=None):
    return jinja2.Markup(logic.game_info_url(account_id=account.id if account is not None else None,
                                             client_turns=client_turns))


@jinja2.jinjaglobal
def game_diary_url():
    return jinja2.Markup(logic.game_diary_url())


@jinja2.jinjaglobal
def game_names_url():
    return jinja2.Markup(logic.game_names_url())


@jinja2.jinjaglobal
def game_hero_history_url():
    return jinja2.Markup(logic.game_hero_history_url())


@jinja2.jinjafilter
def verbose_game_date(turn_number):
    return turn.game_datetime(turn_number).date.verbose_full()


@jinja2.jinjaglobal
def game_datetime(turn_number=None):
    return turn.game_datetime(turn_number)


@jinja2.jinjaglobal
def communication_abilities(mob):
    levels = []

    if mob.communication_verbal.is_CAN:
        levels.append('вербальная')

    if mob.communication_gestures.is_CAN:
        levels.append('невербальная')

    if mob.communication_telepathic.is_CAN:
        levels.append('телепатия')

    if not levels:
        levels.append('—')

    return ', '.join(levels)
