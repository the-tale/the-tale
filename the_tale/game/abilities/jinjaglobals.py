# coding: utf-8

import jinja2

from dext.jinja2.decorators import jinjaglobal

from the_tale.game.abilities import logic

@jinjaglobal
def use_ability_url(ability, building=None, battle=None):
    return jinja2.Markup(logic.use_ability_url(ability=ability, building=building, battle=battle))
