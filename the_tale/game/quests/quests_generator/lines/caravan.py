# coding: utf-8
from ..quest_line import Quest, Line, ACTOR_TYPE
from .. import commands as cmd

class EVENTS:
    INTRO = 'intro'
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

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Caravan, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('choose_point_1', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[cmd.Battle(number=1, event=EVENTS.CARAVAN_ATTACK),
                                    cmd.Move(place=self.env_local.place_start, event=EVENTS.RUN_AWAY),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.Battle(number=2, event=EVENTS.BANDITS_ATTACK),
                                     cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_POINT),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        main_line = Line(sequence=[cmd.Message(event=EVENTS.INTRO),
                                   cmd.Move(place=self.env_local.place_end, break_at=0.5, event=EVENTS.MOVE_TO_POINT),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'caravan': env.new_line(good_line_2),
                                                       'bandits': env.new_line(bad_line_1)},
                                              event=EVENTS.BRING_CHOICE,
                                              choice='bring') ])
        self.line = env.new_line(main_line)
