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

    ACTIONS = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя доставить %(item_to_deliver)s для %(person_end)s в %(place_end)s',
                EVENTS.MOVE_TO_DESTINATION: u'Герой доставляет %(item_to_deliver)s в %(place_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя доставить %(item_to_deliver)s для %(person_end)s в %(place_end)s',
            EVENTS.GET_ITEM: u'Герой получил %(item_to_deliver)s',
            EVENTS.MOVE_TO_DESTINATION: u'Работа у курьеров не простая, пора двигаться в %(place_end)s',
            EVENTS.GIVE_ITEM: u'Герой вручил %(item_to_deliver)s %(person_end)s',
            EVENTS.GET_REWARD: u'%(person_end)s вручил герою награду',
            EVENTS.STEAL_REWARD: u'Теперь %(item_to_deliver)s будет моим',
            EVENTS.STEAL_CHOICE: u'Доставить или украсть - вот в чём вопрос'}

    CHOICES = { CHOICES.STEAL: {'question': u'Зачем <a href="#" class="pgf-choice" data-choice="delivery">мучаться с доставкой</a> %(item_to_deliver)s если можно  <a href="#" class="pgf-choice" data-choice="steal">урасть</a> посылку?',
                                'results': {'delivery': u'Герой решил честно выполнить условия сделки',
                                            'steal': u'Герой решил присвоить %(item_to_deliver)s'} 
                                } 
                }
