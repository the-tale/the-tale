

class Property:
    __slots__ = ('object_id', 'type', 'value')

    def __init__(self, object_id, type, value):
        self.object_id = object_id
        self.type = type
        self.value = value

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
