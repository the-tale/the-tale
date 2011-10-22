# coding: utf-8
from ..quest_line import QuestLine
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    GET_ITEM = 'get_item'
    MOVE_TO_DESTINATION = 'move_to_destination'
    GIVE_ITEM = 'give_item'
    GET_REWARD = 'get_reward'


class DeliveryLine(QuestLine):

    def initialize(self, env, **kwargs):
        super(DeliveryLine, self).__init__(env, **kwargs)
        self.env.register('item_to_deliver', env.new_item())

    def create_line(self, env):
        self.line = [ cmd.GetItem(self.env.item_to_deliver, event=EVENTS.GET_ITEM),
                      cmd.Move(place=self.env.place_end, event=EVENTS.MOVE_TO_DESTINATION),
                      cmd.GiveItem(self.env.item_to_deliver, event=EVENTS.GIVE_ITEM),
                      cmd.GetReward(person=self.env.person_end, event=EVENTS.GET_REWARD)]


class DeliveryWriter(Writer):

    QUEST_TYPE = DeliveryLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
                EVENTS.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to deliver %(item_to_deliver)s to %(person_end)s in %(place_end)s',
            EVENTS.GET_ITEM: 'QUEST: hero get %(item_to_deliver)s',
            EVENTS.MOVE_TO_DESTINATION: 'QUEST: hero is delivering to %(place_end)s',
            EVENTS.GIVE_ITEM: 'QUEST: hero give %(item_to_deliver)s to %(person_end)s',
            EVENTS.GET_REWARD: 'QUEST: %(person_end)s give gero a reward' }
