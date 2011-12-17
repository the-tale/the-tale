# coding: utf-8
from ..quest_line import Quest, Line
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_POINT = 'move_to_point'
    BANDITS_ATTACK = 'bandits_attack'
    GET_REWARD = 'get_reward'

    GOOD_GIVE_POWER = 'good_give_power'

# class CHOICES:
#     STEAL = 'steal'

class CaravanLine(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(CaravanLine, self).initialize(identifier, env, **kwargs)
        # self.env_local.register('item_to_deliver', env.new_item())
        # self.env_local.register('steal_point', env.new_choice_point())

    def create_line(self, env):
        main_line = Line(sequence=[cmd.Move(place=self.env_local.place_end, break_at=0.33, event=EVENTS.MOVE_TO_POINT),
                                   cmd.Battle(number=1, event=EVENTS.BANDITS_ATTACK),
                                   cmd.Move(place=self.env_local.place_end, break_at=0.67, event=EVENTS.MOVE_TO_POINT),
                                   cmd.Battle(number=2, event=EVENTS.BANDITS_ATTACK),
                                   cmd.Move(place=self.env_local.place_end, break_at=1.0, event=EVENTS.MOVE_TO_POINT),
                                   cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                   cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                   cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        self.line = main_line


class CaravanWriter(Writer):

    QUEST_TYPE = CaravanLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to accompany the caravan to %(person_end)s in %(place_end)s',
                EVENTS.MOVE_TO_POINT: 'QUEST: hero is moving with caravan to %(place_end)s',
                EVENTS.BANDITS_ATTACK: 'QUEST: hero is defending the caravan'}

    LOG = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to  accompany the caravan to %(person_end)s in %(place_end)s',
            EVENTS.MOVE_TO_POINT: 'QUEST: hero is moving with caravan to %(place_end)s',
            EVENTS.BANDITS_ATTACK: 'QUEST: caravan is under attack',
            EVENTS.GET_REWARD: 'QUEST: %(person_end)s give hero a reward'}

    # CHOICES = { CHOICES.STEAL: {'question': 'should hero <a href="#" class="pgf-choice" data-choice="delivery">deliver</a> %(item_to_deliver)s or <a href="#" class="pgf-choice" data-choice="steal">steal</a> it?',
    #                             'results': {'delivery': 'hero desided to deliver %(item_to_deliver)s',
    #                                         'steal': 'hero desided to steal %(item_to_deliver)s'} 
    #                             } 
    #             }
