# coding: utf-8
import random

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd

class EVENTS:
    INTRO = 'intro'
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    MOVE_TO_CUSTOMER = 'move_to_customer'
    START_QUEST = 'start_quest'
    GIVE_POWER_TO_CUSTOMER = 'give_power_to_customer'
    GET_POWER_FROM_PERFORMER = 'get_power_from_performer'
    ATTACK_PERFORMER = 'brutforce_performer'
    WORK_CHOICE = 'diplomacy_choice'
    GET_REWARD = 'get_reward'

    CHOICE_DO_WORK = 'choice_do_work'
    CHOICE_ATTACK = 'choice_attack'


class NotMyWork(Quest):

    ACTORS = [(u'попросил', 'person_start', ACTOR_TYPE.PERSON),
              (u'должник', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(NotMyWork, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('choose_point_1', env.new_choice_point())
        self.env_local.register('others_work_quest', env.new_quest(from_list=['delivery', 'caravan', 'spying'],
                                                                   place_start=self.env_local.place_end,
                                                                   person_start=self.env_local.person_end) )

    def create_line(self, env):
        env.quests[self.env_local.others_work_quest].create_line(env)

        work_line = Line(sequence=[ cmd.Message(event=EVENTS.CHOICE_DO_WORK),
                                    cmd.Quest(quest=self.env_local.others_work_quest, event=EVENTS.START_QUEST),
                                    cmd.Move(place=self.env_local.place_start, event=EVENTS.MOVE_TO_CUSTOMER),
                                    cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GIVE_POWER_TO_CUSTOMER),
                                    cmd.GetReward(person=self.env_local.person_start, event=EVENTS.GET_REWARD),
                                    ] )

        attack_line =  Line(sequence=[ cmd.Message(event=EVENTS.CHOICE_ATTACK),
                                       cmd.Battle(number=random.randint(1, 5), event=EVENTS.ATTACK_PERFORMER),
                                       cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.GET_POWER_FROM_PERFORMER),
                                       cmd.Move(place=self.env_local.place_start, event=EVENTS.MOVE_TO_CUSTOMER),
                                       cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GIVE_POWER_TO_CUSTOMER),
                                       cmd.GetReward(person=self.env_local.person_start, event=EVENTS.GET_REWARD),
                                       ] )

        main_line = Line(sequence=[cmd.Message(event=EVENTS.INTRO),
                                   cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'diplomacy': env.new_line(work_line),
                                                       'bruteforce': env.new_line(attack_line)},
                                              event=EVENTS.WORK_CHOICE,
                                              choice='work') ])

        self.line = env.new_line(main_line)
