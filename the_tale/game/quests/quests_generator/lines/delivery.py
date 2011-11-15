# coding: utf-8
from ..quest_line import Quest, Line
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    GET_ITEM = 'get_item'
    MOVE_TO_DESTINATION = 'move_to_destination'
    GIVE_ITEM = 'give_item'
    GET_REWARD = 'get_reward'
    STEAL_REWARD = 'steal_reward'
    STEAL_CHOICE = 'steal_choice'

    GOOD_GIVE_POWER = 'good_give_power'
    EVIL_GIVE_POWER = 'evil_give_power'

class CHOICES:
    STEAL = 'steal'

class DeliveryLine(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(DeliveryLine, self).initialize(identifier, env, **kwargs)
        self.env_local.register('item_to_deliver', env.new_item())
        self.env_local.register('steal_point', env.new_choice_point())

    def create_line(self, env):
        delivery_line = Line(sequence=[cmd.GiveItem(self.env_local.item_to_deliver, event=EVENTS.GIVE_ITEM),
                                       cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                       cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                       cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])
        steal_line = Line(sequence=[cmd.GetReward(event=EVENTS.STEAL_REWARD),
                                    cmd.GiveItem(self.env_local.item_to_deliver, event=EVENTS.GIVE_ITEM),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.EVIL_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.EVIL_GIVE_POWER)])

        self.line = Line(sequence=[ cmd.GetItem(self.env_local.item_to_deliver, event=EVENTS.GET_ITEM),
                                    cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_DESTINATION),
                                    cmd.Choose(id=self.env_local.steal_point,
                                               default='delivery',
                                               choices={'delivery': env.new_line(delivery_line),
                                                        'steal': env.new_line(steal_line)},
                                               event=EVENTS.STEAL_CHOICE,
                                               choice=CHOICES.STEAL) ])


class DeliveryWriter(Writer):

    QUEST_TYPE = DeliveryLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
                EVENTS.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
            EVENTS.GET_ITEM: 'QUEST: hero get %(item_to_deliver)s',
            EVENTS.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s',
            EVENTS.GIVE_ITEM: 'QUEST: hero give %(item_to_deliver)s to %(person_end)s',
            EVENTS.GET_REWARD: 'QUEST: %(person_end)s give gero a reward',
            EVENTS.STEAL_REWARD: 'QUEST: hero steal %(item_to_deliver)s',
            EVENTS.STEAL_CHOICE: 'QUEST: hero is desiding to steal or not to steal'}

    CHOICES = { CHOICES.STEAL: {'question': 'should hero <a href="#" class="pgf-choice" data-choice="delivery">deliver</a> %(item_to_deliver)s or <a href="#" class="pgf-choice" data-choice="steal">steal</a> it?',
                                'results': {'delivery': 'hero desided to deliver %(item_to_deliver)s',
                                            'steal': 'hero desided to steal %(item_to_deliver)s'} 
                                } 
                }
