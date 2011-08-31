#!/usr/bin/python
# coding: utf-8

from game.quests.quests_generator.environment import Environment
from game.quests.quests_generator.sequence import Sequence

from game.quests.quests_generator import story_points as sp

env = Environment()

seq = Sequence(env, [sp.Quest()])

seq.mutate()
seq.mutate()
seq.mutate()

output = [el.__class__.__name__ for el in seq.seq]

print output
