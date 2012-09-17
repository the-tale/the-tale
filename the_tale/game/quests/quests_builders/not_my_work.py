# coding: utf-8
import random

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd

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
        self.env_local.register('others_work_quest', env.new_quest(place_start=self.env_local.place_end,
                                                                   person_start=self.env_local.person_end) )

    def create_line(self, env):
        env.quests[self.env_local.others_work_quest].create_line(env)

        work_positive_line = Line(sequence=[cmd.Message(event='work_quest_successed')])

        # ok, at that line we believe, that person satisfied on any result of child quest
        work_negative_line = Line(sequence=[cmd.Message(event='work_quest_failed')])

        work_line = Line(sequence=[ cmd.Message(event='choice_do_work'),
                                    cmd.Quest(quest=self.env_local.others_work_quest, event='start_quest'),
                                    cmd.Move(place=self.env_local.place_start, event='move_to_customer'),
                                    cmd.Switch(choices=[((self.env_local.others_work_quest, DEFAULT_RESULTS.POSITIVE), env.new_line(work_positive_line)),
                                                        ((self.env_local.others_work_quest, DEFAULT_RESULTS.NEGATIVE), env.new_line(work_negative_line))])
                                    ] )

        attack_line =  Line(sequence=[ cmd.Message(event='choice_attack'),
                                       cmd.Battle(number=random.randint(1, 5), event='attack_performer'),
                                       cmd.GivePower(person=self.env_local.person_end, power=-1, event='get_power_from_performer') ])

        main_line = Line(sequence=[ cmd.Message(event='intro'),
                                    cmd.Move(place=self.env_local.place_end, event='move_to_quest'),
                                    cmd.Choose(id=self.env_local.choose_point_1,
                                               choices={'diplomacy': env.new_line(work_line),
                                                        'bruteforce': env.new_line(attack_line)},
                                               event='work_choice',
                                               choice='work'),
                                    cmd.Move(place=self.env_local.place_start, event='move_to_customer'),
                                    cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                    cmd.GivePower(person=self.env_local.person_start, power=1),
                                    cmd.GetReward(person=self.env_local.person_start, event='get_reward')] )

        self.line = env.new_line(main_line)
