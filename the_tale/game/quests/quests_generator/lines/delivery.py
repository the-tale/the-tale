# coding: utf-8

from ..quest_line import QuestLine
from .. import commands as cmd

class DeliveryLine(QuestLine):

    DESCRIPTION = '<person_start> request to deliver <item_to_deliver> to <person_end> in <place_end>'

    def __init__(self, env, **kwargs):
        super(DeliveryLine, self).__init__(env, **kwargs)

        self.env.register('item_to_deliver', env.new_item())

    def create_line(self, env):
        self.line = [ cmd.GetItem(self.env.item_to_deliver),
                      cmd.Move(place=self.env.place_end),
                      cmd.GiveItem(self.env.item_to_deliver),
                      cmd.GetReward(person=self.env.person_end)]

