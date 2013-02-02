# coding: utf-8

from game.balance import constants as c, enums as e

from game.pvp.exceptions import PvPException

class CombatStyle(object):

    def __init__(self, type_):
        self.type = type_
        self.name = e.PVP_COMBAT_STYLES._ID_TO_TEXT[type_]
        self.str_id = e.PVP_COMBAT_STYLES._ID_TO_STR[type_]
        self.effectiveness = 1.0
        self.cost_rage = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.RAGE]
        self.cost_initiative = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.INITIATIVE]
        self.cost_concentration = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.CONCENTRATION]

        self.advantages = sorted( c.PVP_COMBAT_STYLES_ADVANTAGES[type_].items() , key=lambda x: -x[1])

    def hero_has_resources(self, hero):
        return ( self.cost_rage <= hero.pvp.rage and
                 self.cost_initiative <= hero.pvp.initiative and
                 self.cost_concentration <= hero.pvp.concentration )

    def apply_to_hero(self, hero):
        if not self.hero_has_resources(hero):
            raise PvPException('try to apply pvp combat style to hero with not enough resources. hero: %d style: %d' % (hero.id, self.type))

        hero.pvp.rage -= self.cost_rage
        hero.pvp.initiative -= self.cost_initiative
        hero.pvp.concentration -= self.cost_concentration
        hero.pvp.combat_style = self.type
        hero.pvp.effectiveness = self.effectiveness * (1 + hero.might_pvp_effectiveness_bonus)

    def _give_resources_to_hero(self, hero):
        '''
        for test purpose only
        '''
        hero.pvp.rage = self.cost_rage
        hero.pvp.initiative = self.cost_initiative
        hero.pvp.concentration = self.cost_concentration


COMBAT_STYLES = dict( (style_id, CombatStyle(style_id)) for style_id in e.PVP_COMBAT_STYLES._ALL)
