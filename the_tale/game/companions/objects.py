# coding: utf-8

from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names



class Companion(object):
    __slots__ = ('record', 'health', 'coherence')

    def __init__(self, record, health, coherence):
        self.record = record
        self.health = health
        self.coherence = coherence

    def serialize(self):
        return {'record': self.record.id,
                'health': self.health,
                'coherence': self.coherence}

    @classmethod
    def deserialize(cls, data):
        from the_tale.game.companions import storage
        obj = cls(record=storage.companions[data['record']],
                  health=data['health'],
                  coherence=data['coherence'])
        return obj

    @property
    def name(self): return self.record.name

    @property
    def utg_name(self): return self.record.utg_name

    @property
    def max_health(self): return self.record.max_health


    def ui_info(self):
        return {'name': self.name,
                'health': self.health,
                'max_health': self.max_health,
                'coherence': self.coherence}


class CompanionRecord(names.ManageNameMixin):
    __slots__ = ('id', 'state', 'data', 'type', 'max_health', 'dedication', 'rarity')

    def __init__(self,
                 id,
                 state,
                 data,
                 type,
                 max_health,
                 dedication,
                 rarity):
        self.id = id
        self.state = state
        self.data = data
        self.type = type
        self.max_health = max_health
        self.dedication = dedication
        self.rarity = rarity

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id,
                   state=model.state,
                   data=s11n.from_json(model.data),
                   type=model.type,
                   max_health=model.max_health,
                   dedication=model.dedication,
                   rarity=model.rarity)


    def get_description(self): return self.data['description']
    def set_description(self, value): self.data['description'] = value
    description = property(get_description, set_description)

    @property
    def description_html(self): return bbcode.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field) == getattr(other, field)
                   for field in self.__slots__)
