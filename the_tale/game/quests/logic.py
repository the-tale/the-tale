# -*- coding: utf-8 -*-

from .environment import Environment
# from .quests_generator.lines import QUESTS

from .prototypes import QuestPrototype
from .quests_generator.lines import BaseQuestsSource, BaseWritersSouece
# from .writers import QUEST_WRITERS

def create_random_quest_for_hero(hero):

    env = Environment(quests_source=BaseQuestsSource(),
                      writers_source=BaseWritersSouece())
    env.new_quest()
    env.create_lines()

    # quest_line.set_writer(QUEST_WRITERS)
    
    quest_prototype = QuestPrototype.create(hero, env)

    return quest_prototype
