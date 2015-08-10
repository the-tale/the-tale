# coding: utf-8

from dext.common.utils import jinja2

from the_tale.game import logic
from the_tale.game.prototypes import GameTime


@jinja2.jinjaglobal
def game_info_url(account=None, client_turns=None):
    return jinja2.Markup(logic.game_info_url(account_id=account.id if account is not None else None,
                                             client_turns=client_turns))


@jinja2.jinjafilter
def verbose_game_date(turn):
    return GameTime.create_from_turn(turn).verbose_date


@jinja2.jinjaglobal
def communication_abilities(mob):
    levels = []

    if mob.communication_verbal.is_CAN:
        levels.append(u'вербальная')

    if mob.communication_gestures.is_CAN:
        levels.append(u'невербальная')

    if mob.communication_telepathic.is_CAN:
        levels.append(u'телепатия')

    if not levels:
        levels.append(u'—')

    return u', '.join(levels)
