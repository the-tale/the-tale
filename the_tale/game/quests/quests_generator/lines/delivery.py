# coding: utf-8

from ..quest_line import QuestLine
from .. import commands as cmd

class EVENT_ID:
    QUEST_DESCRIPTION = 'quest_description'
    GET_ITEM = 'get_item'
    MOVE_TO_DESTINATION = 'move_to_destination'
    GIVE_ITEM = 'give_item'
    GET_REWARD = 'get_reward'


class DeliveryLine(QuestLine):

    def __init__(self, env, **kwargs):
        super(DeliveryLine, self).__init__(env, **kwargs)

        self.env.register('item_to_deliver', env.new_item())

    def create_line(self, env):
        self.line = [ cmd.GetItem(self.env.item_to_deliver, event=EVENT_ID.GET_ITEM),
                      cmd.Move(place=self.env.place_end, event=EVENT_ID.MOVE_TO_DESTINATION),
                      cmd.GiveItem(self.env.item_to_deliver, event=EVENT_ID.GIVE_ITEM),
                      cmd.GetReward(person=self.env.person_end, event=EVENT_ID.GET_REWARD)]

