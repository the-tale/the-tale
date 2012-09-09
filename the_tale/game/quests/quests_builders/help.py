# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd

class EVENTS:
    INTRO = 'intro'
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    START_QUEST = 'start_quest'
    GIVE_POWER = 'give_power'

class Help(Quest):

    ACTORS = [(u'попросил', 'person_start', ACTOR_TYPE.PERSON),
              (u'нуждающийся', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Help, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('quest_help', env.new_quest(from_list=['delivery', 'caravan', 'spying', 'not_my_work'],
                                                            place_start=self.env_local.place_end,
                                                            person_start=self.env_local.person_end) )

    def create_line(self, env):
        main_line =  Line(sequence= [ cmd.Message(event=EVENTS.INTRO),
                                      cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                      cmd.Quest(quest=self.env_local.quest_help, event=EVENTS.START_QUEST),
                                      cmd.GivePower(person=self.env_local.person_start,
                                                    depends_on=self.env_local.person_end, multiply=0.25,
                                                    event=EVENTS.GIVE_POWER)])
        self.line = env.new_line(main_line)
        env.quests[self.env_local.quest_help].create_line(env)
