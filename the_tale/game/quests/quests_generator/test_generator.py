#!/usr/bin/python
# coding: utf-8

import random
import pprint

from game.quests.quests_generator.environment import Environment
from game.quests.quests_generator.lines import QUESTS

env = Environment()

quest = random.choice(QUESTS)(env=env)

quest.create_line(env)

description = quest.get_description()

pprint.pprint(description)
