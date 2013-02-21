# coding: utf-8

from game.prototypes import TimePrototype

from game.chronicle.models import Record, RECORD_TYPE


class RecordPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def id(self): return self.model.id

    def get_type(self):
        if not hasattr(self, '_type'):
            self._type = RECORD_TYPE(self.model.type)
        return self._type
    def set_type(self, value):
        self.type.update(value)
        self.model.type = self.type.value
    type = property(get_type, set_type)

    @property
    def text(self): return self.model.text

    @property
    def game_time(self):
        return TimePrototype(self.model.created_at_turn).game_time


    @classmethod
    def create(cls, record):

        model = Record.objects.create(type=record.TYPE,
                                      text=record.get_text(),
                                      created_at_turn=record.created_at_turn)

        return cls(model)
