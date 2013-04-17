# coding: utf-8

from common.utils.discovering import discover_classes


class BasePvPAbility(object):
    TYPE = None
    NAME = None
    DESCRIPTION = None

    def __init__(self, hero, enemy):
        self.hero = hero
        self.enemy = enemy

    @property
    def has_resources(self): return self.hero.pvp.energy > 0

    @staticmethod
    def get_probability(energy): return max(0.01, (100 - energy) / 100.0)

    @property
    def probability(self): return self.get_probability(self.hero.pvp.energy)

    def modify_effect(self, effect): return effect * 1.0/self.probability

    def apply(self): raise NotImplemented



class Ice(BasePvPAbility):
    TYPE = 'ice'
    NAME = u'Лёд'
    DESCRIPTION = u'Сконцентрироваться и увеличить прирост энергии'

    def apply(self):
        self.hero.pvp.energy_speed += int(round(self.modify_effect(1)))
        self.hero.pvp.energy = 0


class Blood(BasePvPAbility):
    TYPE = 'blood'
    NAME = u'Кровь'
    DESCRIPTION = u'Усилить связь с героем и увеличить его эффективность'

    def apply(self):
        self.hero.pvp.effectiveness += int(round(self.modify_effect(1.0)*(1 + self.hero.might_pvp_effectiveness_bonus)))
        self.hero.pvp.energy = 0


class Flame(BasePvPAbility):
    TYPE = 'flame'
    NAME = u'Пламя'
    DESCRIPTION = u'Нарушить концентрацию противника и уменьшить прирост его энергии'

    def apply(self):
        self.enemy.pvp.energy_speed -= int(round(self.modify_effect(1.0)))
        if self.enemy.pvp.energy_speed < 1:
            self.enemy.pvp.energy_speed = 1
        self.hero.pvp.energy = 0


ABILITIES = {ability.TYPE:ability
             for ability in discover_classes(globals().values(), BasePvPAbility)}
