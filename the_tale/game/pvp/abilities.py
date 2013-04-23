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
    def get_probability(energy, energy_speed): raise NotImplemented

    @property
    def probability(self): return self.get_probability(self.hero.pvp.energy, self.hero.pvp.energy_speed)

    def apply(self): raise NotImplemented

    def miss(self):
        self.hero.pvp.energy = 0
        self.hero.add_message('pvp_miss_ability', hero=self.hero)
        self.enemy.add_message('pvp_miss_ability', turn_delta=1, hero=self.hero)


class Ice(BasePvPAbility):
    TYPE = 'ice'
    NAME = u'Лёд'
    DESCRIPTION = u'Сконцентрироваться и увеличить прирост энергии'

    @staticmethod
    def get_probability(energy, energy_speed): return min(1.0, energy * 10 / 100.0 / energy_speed)

    def apply(self):
        self.hero.pvp.energy_speed += 1
        self.hero.pvp.energy = 0
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, hero=self.hero)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, hero=self.hero)



class Blood(BasePvPAbility):
    TYPE = 'blood'
    NAME = u'Кровь'
    DESCRIPTION = u'Усилить связь с героем и увеличить его эффективность'

    @staticmethod
    def get_probability(energy, energy_speed): return max(0.01, (100 - energy) / 100.0)

    # expected value = effect * probability => effect = expected / probability
    # and mutliply by "turns number" (~ total energy)
    def modify_effect(self, expected): return self.hero.pvp.energy * expected / self.probability

    def apply(self):
        effectiveness_delta = int(round(100 * self.modify_effect(1.0)*(1 + self.hero.might_pvp_effectiveness_bonus)))
        self.hero.pvp.effectiveness += effectiveness_delta
        self.hero.pvp.energy = 0
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, hero=self.hero, effectiveness=effectiveness_delta)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, hero=self.hero, effectiveness=effectiveness_delta)


class Flame(BasePvPAbility):
    TYPE = 'flame'
    NAME = u'Пламя'
    DESCRIPTION = u'Нарушить концентрацию противника и уменьшить прирост его энергии'

    @staticmethod
    def get_probability(energy, energy_speed): return min(1.0, energy * 10 / 100.0 / energy_speed)

    def apply(self):
        if self.enemy.pvp.energy_speed > 1:
            self.enemy.pvp.energy_speed -= 1
        self.hero.pvp.energy = 0
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, hero=self.hero)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, hero=self.hero)


ABILITIES = {ability.TYPE:ability
             for ability in discover_classes(globals().values(), BasePvPAbility)}
