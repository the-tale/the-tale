# -*- coding: utf-8 -*-
import random

from .environment import Environment
from .quests_generator.lines import QUESTS

from .prototypes import QuestPrototype
from .writers import QUEST_WRITERS

def create_random_quest_for_hero(hero):
    env = Environment()
    quest_line = random.choice(QUESTS)(env=env)
    quest_line.create_line(env)
    quest_line.set_writer(QUEST_WRITERS)
    
    quest = QuestPrototype.create(hero, env, quest_line)

    return quest
