# coding: utf-8
from ..quest_line import Quest, Line, ACTOR_TYPE
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    GET_ITEM = 'get_item'
    MOVE_TO_DESTINATION = 'move_to_destination'
    GIVE_ITEM = 'give_item'
    STEAL_ITEM = 'steal_item'
    GET_REWARD = 'get_reward'
    STEAL_REWARD = 'steal_reward'
    STEAL_CHOICE = 'steal_choice'

    GOOD_GIVE_POWER = 'good_give_power'
    EVIL_GIVE_POWER = 'evil_give_power'


class Delivery(Quest):

    ACTORS = [(u'отправитель', 'person_start', ACTOR_TYPE.PERSON),
              (u'получатель', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, **kwargs):
        super(Delivery, self).initialize(identifier, env, **kwargs)
        self.env_local.register('item_to_deliver', env.new_item())
        self.env_local.register('steal_point', env.new_choice_point())

    def create_line(self, env):
        delivery_line = Line(sequence=[cmd.GiveItem(self.env_local.item_to_deliver, event=EVENTS.GIVE_ITEM),
                                       cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                       cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                       cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])
        steal_line = Line(sequence=[cmd.GetReward(event=EVENTS.STEAL_REWARD),
                                    cmd.GiveItem(self.env_local.item_to_deliver, event=EVENTS.STEAL_ITEM),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.EVIL_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.EVIL_GIVE_POWER)])

        main_line = Line(sequence=[ cmd.GetItem(self.env_local.item_to_deliver, event=EVENTS.GET_ITEM),
                                    cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_DESTINATION),
                                    cmd.Choose(id=self.env_local.steal_point,
                                               choices={'delivery': env.new_line(delivery_line),
                                                        'steal': env.new_line(steal_line)},
                                               event=EVENTS.STEAL_CHOICE,
                                               choice='steal') ])

        self.line = env.new_line(main_line)
