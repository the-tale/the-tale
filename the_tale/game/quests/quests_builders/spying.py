# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd

class Spying(Quest):

    ACTORS = [(u'заказчик', 'person_start', ACTOR_TYPE.PERSON),
              (u'цель', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Spying, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('choose_point_1', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[ cmd.Message(event='choice_open_up'),
                                     cmd.MoveNear(place=self.env_local.place_end, back=True),
                                     cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                     cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                     cmd.GivePower(person=self.env_local.person_start, power=-1),
                                     cmd.GivePower(person=self.env_local.person_end, power=1)])

        good_line_2 = Line(sequence=[cmd.Message(event='choice_continue_spying'),
                                     cmd.MoveNear(place=self.env_local.place_end, back=True),
                                     cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                     cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                     cmd.GivePower(person=self.env_local.person_start, power=1),
                                     cmd.GivePower(person=self.env_local.person_end, power=-1)])

        main_line = Line(sequence=[cmd.Message(event='intro'),
                                   cmd.Move(place=self.env_local.place_end, event='move_to_quest'),
                                   cmd.MoveNear(place=self.env_local.place_end, back=False, event='spying'),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'spy': env.new_line(good_line_2),
                                                       'open_up': env.new_line(bad_line_1)},
                                              event='open_up_choice',
                                              choice='openup') ])
        self.line = env.new_line(main_line)
