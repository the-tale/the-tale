# coding: utf-8

import jinja2

from dext.jinja2.decorators import jinjaglobal, jinjafilter

from the_tale.game import logic
from the_tale.game.prototypes import GameTime


@jinjaglobal
def game_info_url(account=None):
    return jinja2.Markup(logic.game_info_url(account_id=account.id if account is not None else None))


@jinjafilter
def verbose_game_date(turn):
    return GameTime.create_from_turn(turn).verbose_date
