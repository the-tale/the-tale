# coding: utf-8

from ..writer import Writer

from .help import HelpLine, HelpWriter
from .delivery import DeliveryLine, DeliveryWriter
from .caravan import CaravanLine, CaravanWriter

QUESTS = [HelpLine, DeliveryLine, CaravanLine]
QUESTS = [CaravanLine]

__all__ = ['QUESTS', 'HelpLine', 'DeliveryLine', 'CaravanLine']

class BaseQuestsSource:
    
    quests_list = QUESTS

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None


QUEST_WRITERS = {HelpLine.type(): [ HelpWriter ],
                 DeliveryLine.type(): [DeliveryWriter],
                 CaravanLine.type(): [CaravanWriter]}

WRITERS = dict( (writer.type(), writer) 
                for writer_name, writer in globals().items()
                if isinstance(writer, type) and issubclass(writer, Writer))

class BaseWritersSouece:

    quest_writers = QUEST_WRITERS

    writers = WRITERS
