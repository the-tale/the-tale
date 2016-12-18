# coding: utf-8

from dext.common.utils import jinja2

from the_tale.game.abilities import logic

@jinja2.jinjaglobal
def use_ability_url(ability, building=None, battle=None):
    return jinja2.Markup(logic.use_ability_url(ability=ability, building=building, battle=battle))
