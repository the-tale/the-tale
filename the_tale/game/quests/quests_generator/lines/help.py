# coding: utf-8
from ..quest_line import QuestLine
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    START_QUEST = 'start_quest'

class HelpLine(QuestLine):

    def initialize(self, env, **kwargs):
        super(HelpLine, self).__init__(env, **kwargs)

        self.env.register('quest_help', env.new_quest(place_start=self.env.place_end,
                                                      person_start=self.env.person_end) )

    def create_line(self, env):
        self.quest_help.create_line(env)

        self.line =  [ cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                       cmd.Quest(quest=self.quest_help, event=EVENTS.START_QUEST) ]

class HelpWriter(Writer):

    QUEST_TYPE = HelpLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION: 'QUEST: %(person_start)s ask hero to help %(person_end)s from %(place_end)s',
                EVENTS.MOVE_TO_QUEST: 'QUEST: hero is moving to %(place_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION: 'QUEST: %(person_start)s ask hero to help %(person_end)s from %(place_end)s',
            EVENTS.MOVE_TO_QUEST: 'QUEST: hero is moving to %(place_end)s'}
