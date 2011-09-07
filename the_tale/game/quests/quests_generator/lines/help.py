# coding: utf-8
import random

from ..quest_line import QuestLine
from .. import commands as cmd

class HelpLine(QuestLine):

    DESCRIPTION = '<person_start> request help for <person_end> in <place_end>'

    def __init__(self, env, **kwargs):
        from . import QUESTS
        super(HelpLine, self).__init__(env, **kwargs)

        self.quest_help = random.choice(QUESTS)(env,
                                                place_start=self.env.place_end, 
                                                person_start=self.env.person_end)

    def create_line(self, env):
        self.quest_help.create_line(env)

        self.line =  [ cmd.Move(place=self.env.place_end),
                       cmd.Quest(quest=self.quest_help) ]
