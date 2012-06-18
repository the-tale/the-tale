# coding: utf-8
from ..quest_line import Quest, Line, ACTOR_TYPE
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_POINT = 'move_to_point'
    BANDITS_ATTACK = 'bandits_attack'
    CARAVAN_ATTACK = 'caravan_attack'
    GET_REWARD = 'get_reward'
    RUN_AWAY = 'run_away'

    GOOD_GIVE_POWER = 'good_give_power'
    BAD_GIVE_POWER = 'bad_give_power'

    BRING_CHOICE = 'bring_choice'

class Caravan(Quest):

    ACTORS = [(u'отправил', 'person_start', ACTOR_TYPE.PERSON),
              (u'место назначения', 'place_end', ACTOR_TYPE.PLACE),
              (u'ожидает прибытия', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, **kwargs):
        super(Caravan, self).initialize(identifier, env, **kwargs)
        self.env_local.register('choose_point_1', env.new_choice_point())
        self.env_local.register('choose_point_2', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[cmd.Battle(number=1, event=EVENTS.CARAVAN_ATTACK),
                                    cmd.Move(place=self.env_local.place_start, event=EVENTS.RUN_AWAY),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        bad_line_2 = Line(sequence=[cmd.Battle(number=2, event=EVENTS.CARAVAN_ATTACK),
                                    cmd.Move(place=self.env_local.place_end, event=EVENTS.RUN_AWAY),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.Battle(number=2, event=EVENTS.BANDITS_ATTACK),
                                     cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_POINT),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        good_line_1 = Line(sequence=[cmd.Battle(number=1, event=EVENTS.BANDITS_ATTACK),
                                     cmd.Move(place=self.env_local.place_end, break_at=0.67, event=EVENTS.MOVE_TO_POINT),
                                     cmd.Choose(id=self.env_local.choose_point_2,
                                                default='caravan',
                                                choices={'caravan': env.new_line(good_line_2),
                                                         'bandits': env.new_line(bad_line_2)},
                                                event=EVENTS.BRING_CHOICE,
                                                choice='bring') ])

        main_line = Line(sequence=[cmd.Move(place=self.env_local.place_end, break_at=0.33, event=EVENTS.MOVE_TO_POINT),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              default='caravan',
                                              choices={'caravan': env.new_line(good_line_1),
                                                       'bandits': env.new_line(bad_line_1)},
                                              event=EVENTS.BRING_CHOICE,
                                              choice='bring') ])
        self.line = env.new_line(main_line)
