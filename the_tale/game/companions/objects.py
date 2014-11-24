# coding: utf-8

from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names


class CompanionRecord(names.ManageNameMixin):
    __slots__ = ('id', 'state', 'data')

    def __init__(self,
                 id,
                 state,
                 data):
        self.id = id
        self.state = state
        self.data = data

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id,
                   state=model.state,
                   data=s11n.from_json(model.data))

    def get_description(self): return self.data['description']
    def set_description(self, value): self.data['description'] = value
    description = property(get_description, set_description)

    @property
    def description_html(self): return bbcode.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field) == getattr(other, field)
                   for field in self.__slots__)
