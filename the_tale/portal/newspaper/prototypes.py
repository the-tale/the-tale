# coding: utf-8

from dext.utils import s11n

from game.prototypes import TimePrototype

from portal.newspaper.models import NewspaperEvent
from portal.newspaper.events import deserialize_event

class NewspaperEventPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def section(self): return self.model.section

    @property
    def type(self): return self.model.type

    @property
    def created_at(self): return self.model.created_at

    @property
    def created_at_turn(self): return self.model.created_at_turn

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = deserialize_event(s11n.from_json(self.model.data))
        return self._data

    @classmethod
    def create(cls, data):

        model = NewspaperEvent.objects.create( section=data.SECTION,
                                               type=data.TYPE,
                                               data=s11n.to_json(data.serialize()),
                                               created_at_turn=TimePrototype.get_current_turn_number() )

        return cls(model)
