# coding: utf-8
from ..quest_line import Quest, Line, ACTOR_TYPE
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    MOVE_NEAR = 'move_near'
    GET_REWARD = 'get_reward'

    GOOD_GIVE_POWER = 'good_give_power'
    BAD_GIVE_POWER = 'bad_give_power'

    OPEN_UP_CHOICE = 'openup_choice'


class Spying(Quest):

    ACTORS = [(u'заказчик', 'person_start', ACTOR_TYPE.PERSON),
              (u'цель', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, **kwargs):
        super(Spying, self).initialize(identifier, env, **kwargs)
        self.env_local.register('choose_point_1', env.new_choice_point())
        self.env_local.register('choose_point_2', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[ cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        bad_line_2 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        good_line_1 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, event=EVENTS.MOVE_NEAR),
                                     cmd.Choose(id=self.env_local.choose_point_2,
                                                choices={'spy': env.new_line(good_line_2),
                                                         'openup': env.new_line(bad_line_2)},
                                                event=EVENTS.OPEN_UP_CHOICE,
                                                choice='openup') ])

        main_line = Line(sequence=[cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'spy': env.new_line(good_line_1),
                                                       'open_up': env.new_line(bad_line_1)},
                                              event=EVENTS.OPEN_UP_CHOICE,
                                              choice='openup') ])
        self.line = env.new_line(main_line)
