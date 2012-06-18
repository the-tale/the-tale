# coding: utf-8

from .help import Help
from .delivery import Delivery
from .caravan import Caravan
from .spying import Spying
from .not_my_work import NotMyWork

QUESTS = [Help, Delivery, Caravan, Spying, NotMyWork]
QUESTS_TYPES = [quest.type() for quest in QUESTS]

# TODO: WHY no all quest added here?
__all__ = ['QUESTS', 'BaseQuestsSource']

class BaseQuestsSource(object):

    quests_list = QUESTS

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None
