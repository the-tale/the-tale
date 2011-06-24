# -*- coding: utf-8 -*-
import random

from .prototypes import QUESTS_TYPES

def create_random_quest_for_hero(hero):
    quest_prototype = random.choice(QUESTS_TYPES.values())

    return quest_prototype.create(hero)
