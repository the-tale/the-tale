
import smart_imports

smart_imports.all()


class BasePvPAbility(object):
    __slots__ = ('hero', 'enemy', 'hero_pvp', 'enemy_pvp')

    TYPE = NotImplemented
    NAME = NotImplemented
    DESCRIPTION = NotImplemented

    def __init__(self, hero, enemy):
        self.hero = hero
        self.enemy = enemy

        self.hero_pvp, self.enemy_pvp = logic.get_arena_heroes_pvp(self.hero)

    @property
    def has_resources(self):
        return self.hero_pvp.energy > 0

    @staticmethod
    def get_probability(energy, energy_speed):
        raise NotImplementedError

    @property
    def probability(self):
        return self.get_probability(self.hero_pvp.energy, self.hero_pvp.energy_speed)

    def use(self):
        if random.uniform(0, 1.0) < self.probability:
            self.apply()
        else:
            self.miss()

    def apply(self):
        raise NotImplementedError

    def miss(self):
        self.hero_pvp.set_energy(0)
        self.hero.add_message('pvp_miss_ability', duelist_1=self.hero, duelist_2=self.enemy)
        self.enemy.add_message('pvp_miss_ability', turn_delta=1, duelist_1=self.hero, duelist_2=self.enemy)


class Ice(BasePvPAbility):
    TYPE = 'ice'
    NAME = 'Лёд'
    DESCRIPTION = 'Сконцентрироваться и увеличить прирост энергии. Чем дольше копилась энергия, тем вероятнее успех применения способности.'

    @staticmethod
    def get_probability(energy, energy_speed):
        return min(1.0, energy * 10 / 100.0 / energy_speed)

    def apply(self):
        self.hero_pvp.set_energy_speed(self.hero_pvp.energy_speed + 1)
        self.hero_pvp.set_energy(0)
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, duelist_1=self.hero, duelist_2=self.enemy)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, duelist_1=self.hero, duelist_2=self.enemy)


class Blood(BasePvPAbility):
    TYPE = 'blood'
    NAME = 'Кровь'
    DESCRIPTION = 'Усилить связь с героем и увеличить его эффективность. Чем больше энергии накоплено, тем вероятнее неудачное применение способности и тем больше прирост эффективности при удачном применении.'

    @staticmethod
    def get_probability(energy, energy_speed):
        return max(0.01, (100 - energy) / 100.0)

    # expected value = effect * probability => effect = expected / probability
    # and mutliply by "turns number" (~ total energy)
    def modify_effect(self, expected):
        return self.hero_pvp.energy * expected / self.probability

    def apply(self):
        effectiveness_delta = int(round(c.PVP_EFFECTIVENESS_STEP * self.modify_effect(1.0) * (1 + self.hero.might_pvp_effectiveness_bonus)))
        self.hero_pvp.set_effectiveness(self.hero_pvp.effectiveness + effectiveness_delta)
        self.hero_pvp.set_energy(0)
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, duelist_1=self.hero, duelist_2=self.enemy, effectiveness=effectiveness_delta)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, duelist_1=self.hero, duelist_2=self.enemy, effectiveness=effectiveness_delta)


class Flame(BasePvPAbility):
    TYPE = 'flame'
    NAME = 'Пламя'
    DESCRIPTION = 'Нарушить концентрацию противника и уменьшить прирост его энергии. Чем дольше копилась энергия, тем вероятнее успех применения способности. Сбросить прирост энергии меньше 1 нельзя.'

    @staticmethod
    def get_probability(energy, energy_speed):
        return min(1.0, energy * 10 / 100.0 / energy_speed)

    def apply(self):
        if self.enemy_pvp.energy_speed > 1:
            self.enemy_pvp.set_energy_speed(self.enemy_pvp.energy_speed - 1)
        self.hero_pvp.set_energy(0)
        self.hero.add_message('pvp_use_ability_%s' % self.TYPE, duelist_1=self.hero, duelist_2=self.enemy)
        self.enemy.add_message('pvp_use_ability_%s' % self.TYPE, turn_delta=1, duelist_1=self.hero, duelist_2=self.enemy)


ABILITIES = {ability.TYPE: ability
             for ability in utils_discovering.discover_classes(globals().values(), BasePvPAbility)}
