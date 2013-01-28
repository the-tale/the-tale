# coding: utf-8

from game.balance import constants as c, enums as e

from game.pvp.exceptions import PvPException

class CombatStyle(object):

    def __init__(self, type_):
        self.type = type_
        self.name = e.PVP_COMBAT_STYLES._ID_TO_TEXT[type_]
        self.str_id = e.PVP_COMBAT_STYLES._ID_TO_STR[type_]
        self.power = c.PVP_COMBAT_STYLES_POWERS[type_]
        self.cost_rage = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.RAGE]
        self.cost_initiative = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.INITIATIVE]
        self.cost_concentration = c.PVP_COMBAT_STYLES_COSTS[type_][e.PVP_COMBAT_RESOURCES.CONCENTRATION]

        self.advantages = sorted( c.PVP_COMBAT_STYLES_ADVANTAGES[type_].items() , key=lambda x: -x[1])

    def hero_has_resources(self, hero):
        return ( self.cost_rage <= hero.pvp_rage and
                 self.cost_initiative <= hero.pvp_initiative and
                 self.cost_concentration <= hero.pvp_concentration )

    def apply_to_hero(self, hero, enemy_hero):
        if not self.hero_has_resources(hero):
            raise PvPException('try to apply pvp combat style to hero with not enough resources. hero: %d style: %d' % (hero.id, self.type))
        hero.pvp_rage -= self.cost_rage
        hero.pvp_initiative -= self.cost_initiative
        hero.pvp_concentration -= self.cost_concentration
        hero.pvp_combat_style = self.type
        hero.pvp_power = self.power

        hero.update_pvp_power_modified(enemy_hero)
        enemy_hero.update_pvp_power_modified(hero)

    def _give_resources_to_hero(self, hero):
        '''
        for test purpose only
        '''
        hero.pvp_rage = self.cost_rage
        hero.pvp_initiative = self.cost_initiative
        hero.pvp_concentration = self.cost_concentration


COMBAT_STYLES = dict( (style_id, CombatStyle(style_id)) for style_id in e.PVP_COMBAT_STYLES._ALL)
