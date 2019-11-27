

class Effect:
    __slots__ = ('id', 'attribute', 'entity', 'value', 'caption', 'data')

    def __init__(self, id, attribute, entity, value, caption, data):
        self.id = id
        self.attribute = attribute
        self.entity = entity
        self.value = value
        self.caption = caption
        self.data = data

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, field) == getattr(other, field) for field in self.__class__.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
