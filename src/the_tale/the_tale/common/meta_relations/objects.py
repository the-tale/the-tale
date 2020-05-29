
import smart_imports

smart_imports.all()


class MetaType(object):
    __slots__ = ('id',)
    TYPE = NotImplemented
    TYPE_CAPTION = NotImplemented

    def __init__(self, id):
        self.id = id

    @property
    def uid(self):
        return logic.create_uid(self.TYPE, self.id)

    @property
    def tag(self):
        return logic.create_tag(self.TYPE, self.id)

    @property
    def is_unknown(self):
        return self.id is None

    @classmethod
    def create_from_id(cls, id):
        raise NotImplementedError()

    def __eq__(self, other):
        return (self.TYPE == other.TYPE,
                self.id == other.id)

    def __neq__(self, other):
        return not self.__eq__(other)


class MetaRelation(object):
    __slots__ = ('id', 'object_1', 'object_2')
    TYPE = NotImplemented

    def __init__(self, id, object_1, object_2):
        self.id = id
        self.object_1 = object_1
        self.object_2 = object_2
