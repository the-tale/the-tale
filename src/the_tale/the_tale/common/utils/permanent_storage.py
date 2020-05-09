
import smart_imports

smart_imports.all()


class PermanentStorageError(exceptions.TheTaleError):
    pass


class DuplicateInsertError(PermanentStorageError):
    MSG = 'item %(item)r already in storage'


class WrongRelationError(PermanentStorageError):
    MSG = 'try insert wrong relation record %(wrong_relation)r, expected %(expected_relation)s'


class PermanentStorage(object):

    def __init__(self):
        self._data = set()

    def serialize(self):
        return tuple(self._data)

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj._data = set(data)
        return obj

    def insert(self, item):
        if item in self._data:
            raise DuplicateInsertError(item=item)
        self._data.add(item)

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()


class PermanentRelationsStorage(PermanentStorage):
    RELATION = NotImplemented
    VALUE_COLUMN = NotImplemented

    def serialize(self):
        return tuple(getattr(record, self.VALUE_COLUMN) for record in self._data)

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj._data = set(getattr(cls.RELATION, 'index_%s' % cls.VALUE_COLUMN)[value] for value in data)
        return obj

    def insert(self, item):
        if not issubclass(item._relation, self.RELATION):
            raise WrongRelationError(wrong_relation=item, expected_relation=self.RELATION)
        super(PermanentRelationsStorage, self).insert(item)
