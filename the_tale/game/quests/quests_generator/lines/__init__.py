# coding: utf-8

from .help import HelpLine
from .delivery import DeliveryLine
from .caravan import CaravanLine
from .spying import SpyingLine
from .not_my_work import NotMyWorkLine

QUESTS = [HelpLine, DeliveryLine, CaravanLine, SpyingLine, NotMyWorkLine]
QUESTS_TYPES = [quest.type() for quest in QUESTS]

# TODO: WHY no all quest added here?
__all__ = ['QUESTS', 'HelpLine', 'DeliveryLine', 'CaravanLine', 'SpyingLine']

class BaseQuestsSource(object):

    quests_list = QUESTS

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None
