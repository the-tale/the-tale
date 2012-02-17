# -*- coding: utf-8 -*-
import math
import random


from . import ArtifactException
from .prototypes import ArtifactPrototype

class ArtifactConstructor(object):

    TYPE = None
    EQUIP_TYPE = None
    NAME = None

    def __init__(self, basic_points):
        self.basic_points = basic_points
        self.basic_points_spent = 0

    @property
    def total_points_spent(self):
        return self.basic_points_spent # + self.effect_points_spent

    @property
    def total_points(self):
        return self.basic_points #+ self.effect_points

    def generate_name(self):
        if self.NAME:
            return self.NAME
        raise ArtifactException('nither name or name generator defined for artifact constructor: %s' % ArtifactConstructor)


    def generate_artifact(self, quest=False):
        artifact = ArtifactPrototype(tp=self.TYPE, equip_type=self.EQUIP_TYPE, quest=quest)

        artifact.set_name(self.generate_name())
        artifact.set_cost(self.generate_cost())
        artifact.set_power(self.generate_power())

        artifact.basic_points_spent = self.basic_points_spent

        return artifact

    def generate_cost(self):
        return (self.total_points + self.total_points_spent) + 1

    def generate_power(self):
        power = int(math.ceil(self.basic_points / 3))
        self.basic_points_spent = power * 3
        return power


class EQUIP_TYPES:
    WEAPON = 'WEAPON'
    PLATE = 'PLATE'

class UselessThingConstructor(ArtifactConstructor):
    TYPE = 'USELESS_THING'

class WeaponConstructor(ArtifactConstructor):
    TYPE = 'WEAPON'

class ArmorConstructor(ArtifactConstructor):
    TYPE = 'ARMOR'

def generate_loot(loot_list, monster_power, basic_modificator):
    probalities_sum = sum(x[0] for x in loot_list)
    key_number = random.randint(1, probalities_sum)

    constructor_class = None
    for probability, loot_constructor in loot_list:
        if probability >= key_number:
            constructor_class = loot_constructor
            break
        key_number -= probability

    # TODO: move constancs from here
    BASE_RANDOMIZING_PERCENT = 15

    percent_modifier = random.choice([-1, 1]) * BASE_RANDOMIZING_PERCENT / 100.0
    basic_points = monster_power * basic_modificator
    basic_points += int(percent_modifier * basic_points)
   
    constructor = constructor_class(basic_points=basic_points)
    artifact = constructor.generate_artifact()

    return artifact

##########################################
# some test resulted constructors
##########################################

class LetterConstructor(UselessThingConstructor):
    NAME = u'письмо'

class FakeAmuletConstructor(UselessThingConstructor):
    NAME = u'поддельный амулет'

class RatTailConstructor(UselessThingConstructor):
    NAME = u'крысиный хвостик'

class PieceOfCheeseConstructor(UselessThingConstructor):
    NAME = u'кусок сыра'

class BrokenSword(WeaponConstructor):
    NAME = u'сломанный меч'
    EQUIP_TYPE = EQUIP_TYPES.WEAPON

class DecrepitPlate(ArmorConstructor):
    NAME = u'дряхлый доспех'
    EQUIP_TYPE = EQUIP_TYPES.PLATE

