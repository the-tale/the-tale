# coding: utf-8

from .help import Help
from .delivery import Delivery
from .caravan import Caravan
from .spying import Spying
from .not_my_work import NotMyWork
from .hunt import Hunt

QUESTS = [Help, Delivery, Caravan, Spying, NotMyWork, Hunt]
QUESTS_TYPES = [quest.type() for quest in QUESTS]

# TODO: WHY no all quest added here?
__all__ = ['QUESTS', 'BaseQuestsSource']

class BaseQuestsSource(object):

    quests_list = QUESTS

    def filter(self, env, special=None):
        result = []

        for quest in self.quests_list:

            if special is not None and quest.SPECIAL != special:
                continue

            if not quest.can_be_used(env):
                continue

            result.append(quest)

        return result

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None
