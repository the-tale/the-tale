# coding: utf-8

from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c



class Companion(object):
    __slots__ = ('record', 'health', 'coherence', 'experience')

    def __init__(self, record, health, coherence, experience):
        self.record = record
        self.health = health
        self.coherence = coherence
        self.experience = experience

    def serialize(self):
        return {'record': self.record.id,
                'health': self.health,
                'coherence': self.coherence,
                'experience': self.experience}

    @classmethod
    def deserialize(cls, data):
        from the_tale.game.companions import storage
        obj = cls(record=storage.companions[data['record']],
                  health=data['health'],
                  coherence=data['coherence'],
                  experience=data['experience'])
        return obj

    @property
    def name(self): return self.record.name

    @property
    def utg_name_form(self): return self.record.utg_name_form

    def linguistics_restrictions(self):
        return []

    @property
    def max_health(self): return self.record.max_health

    def hit(self): self.health -= 1

    @property
    def is_dead(self): return self.health <= 0


    def add_experience(self, value):
        self.experience += value

        if self.coherence == c.COMPANIONS_MAX_COHERENCE:
            self.experience = min(self.experience, self.experience_to_next_level)
            return

        while self.experience_to_next_level <= self.experience:
            self.experience -= self.experience_to_next_level
            self.coherence += 1

    @property
    def experience_to_next_level(self):
        return f.companions_coherence_for_level(min(self.coherence + 1, c.COMPANIONS_MAX_COHERENCE))


    def ui_info(self):
        return {'id': self.record.id,
                'name': self.name[0].upper() + self.name[1:],
                'health': self.health,
                'max_health': self.max_health,
                'experience': self.experience,
                'experience_to_level': self.coherence_experience_to_next_level,
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
