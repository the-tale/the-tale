
import smart_imports

smart_imports.all()


class Restriction(game_names.ManageNameMixin):
    __slots__ = ('id', 'group', 'external_id', 'name')

    def __init__(self,
                 id,
                 group,
                 external_id,
                 name):
        self.id = id
        self.group = group
        self.external_id = external_id
        self.name = name

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id,
                   group=model.group,
                   external_id=model.external_id,
                   name=model.name)

    def storage_key(self):
        return (self.group.value, self.external_id)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.group == other.group and
                self.external_id == other.external_id and
                self.name == other.name)


class UTGVariable(object):
    __slots__ = ('utg_name_form', 'restrictions')

    def __init__(self, word, restrictions):
        self.utg_name_form = word
        self.restrictions = restrictions

    def linguistics_restrictions(self):
        return self.restrictions
