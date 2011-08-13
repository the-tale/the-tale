# -*- coding: utf-8 -*-
import random

from .prototypes import ArtifactPrototype

from . import ArtifactException

class ArtifactConstructor(object):

    TYPE = None
    SUBTYPE = None
    NAME = None

    EFFECTS_LIST = []

    def __init__(self, basic_points, effect_points):
        self.basic_points = basic_points
        self.basic_points_spent = 0

        self.effect_points = effect_points
        self.effect_points_spent = 0

        self.total_points = basic_points + effect_points
        self.total_points_spent = 0

    def generate_name(self):
        if self.NAME:
            return self.NAME
        raise ArtifactException('nither name or name generator defined for artifact constructor: %s' % ArtifactConstructor)

    def generate_effects(self):
        return []

    def generate_basic_effects(self):
        return []

    def generate_cost(self):
        return 0

    def generate_artifact(self):
        artifact = ArtifactPrototype(tp=self.TYPE)

        artifact.set_name(self.generate_name())
        artifact.set_cost(self.generate_cost())
        artifact.add_effects(self.generate_basic_effects())
        artifact.add_effects(self.generate_effects())

        return artifact
        

class UselessThingConstructor(ArtifactConstructor):
    TYPE = 'USELESS_THING'
    EFFECTS_LIST = ArtifactConstructor.EFFECTS_LIST + []

    def generate_cost(self):
        return (self.total_points + self.total_points_spent) / 2 + 1


def generate_loot(loot_list, monster_power, basic_modificator, effects_modificator, chaoticity):
    probalities_sum = sum(x[0] for x in loot_list)
    key_number = random.randint(1, probalities_sum)

    constructor_class = None
    for probability, loot_constructor in loot_list:
        if probability >= key_number:
            constructor_class = loot_constructor
            break
        key_number -= probability

    # TODO: move constancs from here
    BASE_RANDOMIZING_PERCENT = 10
    CHAOTICITY_MODIFIER = 2.5

    percent_modifier = random.choice([-1, 1]) * (BASE_RANDOMIZING_PERCENT + chaoticity * CHAOTICITY_MODIFIER) / 100.0
    basic_points = monster_power * basic_modificator
    basic_points += int(percent_modifier * basic_points)

    percent_modifier = random.choice([-1, 1]) * (BASE_RANDOMIZING_PERCENT + chaoticity * CHAOTICITY_MODIFIER) / 100.
    effect_points = monster_power * effects_modificator
    effect_points += int(percent_modifier * effect_points)
    
    constructor = constructor_class(basic_points=basic_points, effect_points=effect_points)
    artifact = constructor.generate_artifact()

    return artifact


##########################################
# some test resulted constructors
##########################################

class FakeAmuletConstructor(UselessThingConstructor):
    NAME = u'поддельный амулет'

class PieceOfCheeseConstructor(UselessThingConstructor):
    NAME = u'кусок сыра'

##########################################
# some resulted constructors
##########################################

TEST_LOOT_LIST = [ (1, FakeAmuletConstructor),
                   (2, PieceOfCheeseConstructor)]
