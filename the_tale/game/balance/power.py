# coding: utf-
import collections
import random

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

PowerDistribution = collections.namedtuple('PowerDistribution', ('physic', 'magic'))


class Power(object):
    __slots__ = ('physic', 'magic')

    def __init__(self, physic, magic):
        self.physic = physic
        self.magic = magic

    def serialize(self):
        return [self.physic, self.magic]

    def ui_info(self):
        return [self.physic, self.magic]

    @classmethod
    def deserialize(cls, data):
        return cls(*data)

    @classmethod
    def zero(cls):
        return cls(0, 0)

    def clone(self):
        return self.__class__(physic=self.physic, magic=self.magic)

    @classmethod
    def clean_power_for_hero_level(cls, level):
        half_power = level * c.POWER_PER_LVL / 2 + 1
        return cls(half_power, half_power)

    def total(self):
        return self.magic + self.physic

    # общая ожидаемая сила артефактов, надетых на героя указанного уровня к моменту получения следующего уровня
    # рассматривался альтернативный вариант - зависимость силы, от времени, но в этом случае она растёт очень быстро, что плохо сказывается на цифрах урона и т.п.
    # за ожидаемое распределение берётся нейтральный герой (т.е. без предпочтения в магии/физике)
    # @classmethod
    # def expected_power_to_level(cls, level): # TODO: remove?
    #     print cls.normal_total_power_to_level(level)
    #     half_power = cls.normal_total_power_to_level(level) / 2
    #     return cls(half_power, half_power)

    @classmethod
    def normal_total_power_to_level(cls, level):
        return int(level * c.POWER_TO_LVL)

    @classmethod
    def power_to_artifact(cls, distribution, level):
        power = float(cls.normal_total_power_to_level(level)) / c.EQUIP_SLOTS_NUMBER
        return cls(physic=int(power*distribution.physic+0.5),
                   magic=int(power*distribution.magic+0.5) )

    # функция, для получения случайного значения силы артефакта
    @classmethod
    def artifact_power_interval(cls, distribution, level):
        base_power = cls.power_to_artifact(distribution, level)
        physic_delta = int(base_power.physic * c.ARTIFACT_POWER_DELTA)
        magic_delta = int(base_power.magic * c.ARTIFACT_POWER_DELTA)
        min_power = cls(physic=max(base_power.physic - physic_delta, 1),
                        magic=max(base_power.magic - magic_delta, 1))
        max_power = cls(physic=base_power.physic + physic_delta,
                        magic=base_power.magic + magic_delta)
        return min_power, max_power

    @classmethod
    def artifact_power_randomized(cls, distribution, level):
        min_power, max_power = cls.artifact_power_interval(distribution, level)
        return cls(physic=random.randint(min_power.physic, max_power.physic),
                   magic=random.randint(min_power.magic, max_power.magic))

    # артефакт лучше среднего для магазина
    @classmethod
    def better_artifact_power_randomized(cls, distribution, level):
        base_power = cls.power_to_artifact(distribution, level)
        physic_delta = max(int(base_power.physic * c.ARTIFACT_POWER_DELTA), c.ARTIFACT_BETTER_MIN_POWER_DELTA)
        magic_delta = max(int(base_power.magic * c.ARTIFACT_POWER_DELTA), c.ARTIFACT_BETTER_MIN_POWER_DELTA)
        return cls(physic=random.randint(base_power.physic+1, base_power.physic + 1 + 2 * physic_delta),
                   magic=random.randint(base_power.magic+1, base_power.magic + 1 + 2 * magic_delta))

    # находим зависимость урона, наносимого героем от его силы
    # для этого опираясь на силу, оцениваем уровень героя, на котором она может быть и исходя из этого делаем предположение об уроне мобу
    # т.к. здоровье моба зависит от здоровья героя, то полученая формула должна быть применима и в PvP - т.е. бои просто будут идти дольше
    # делим на 2, т.к. считаем, что обе силы (магическая и физическая) равны
    def expected_levels(self):
        physic = float(self.physic) / (c.POWER_PER_LVL + c.POWER_TO_LVL/2) # оцениваемый уровень героя, исходя из его силы
        magic =  float(self.magic) / (c.POWER_PER_LVL + c.POWER_TO_LVL/2) # оцениваемый уровень героя, исходя из его силы
        return physic, magic

    def damage(self):
        physic_level, magic_level = self.expected_levels()
        return Damage(physic=f.expected_damage_to_mob_per_hit(physic_level) / 2,
                      magic=f.expected_damage_to_mob_per_hit(magic_level) / 2)

    def __repr__(self): return u'Power(physic=%d, magic=%d)' % (self.physic, self.magic)

    def __eq__(self, other):
        return (self.physic == other.physic and
                self.magic == other.magic)

    def __add__(self, other):
        return self.__class__(physic=self.physic + other.physic,
                              magic=self.magic + other.magic)

    def __iadd__(self, other):
        self.physic += other.physic
        self.magic += other.magic
        return self



class Damage(object):
    __slots__ = ('physic', 'magic')

    def __init__(self, physic=0.0, magic=0.0):
        self.physic = physic
        self.magic = magic

    @property
    def total(self): return int(round(self.physic + self.magic))

    def clone(self): return self.__class__(physic=self.physic, magic=self.magic)

    def multiply(self, physic_multiplier=1.0, magic_multiplier=1.0):
        self.physic *= physic_multiplier
        self.magic *= magic_multiplier
        return self

    def randomize(self):
        self.physic =  self.physic * random.uniform(1-c.DAMAGE_DELTA, 1+c.DAMAGE_DELTA)
        self.magic =  self.magic * random.uniform(1-c.DAMAGE_DELTA, 1+c.DAMAGE_DELTA)

    def __mul__(self, other):
        return self.clone().multiply(other, other)

    def __imul__(self, other):
        return self.multiply(other, other)

    def __div__(self, other):
        return self.clone().multiply(1.0/other, 1.0/other)

    def __idiv__(self, other):
        return self.multiply(1.0/other, 1.0/other)

    def __repr__(self): return u'Damage(physic=%f, magic=%f)' % (self.physic, self.magic)

    def __eq__(self, other):
        return (self.physic == other.physic and
                self.magic == other.magic)
