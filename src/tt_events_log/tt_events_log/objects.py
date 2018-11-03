

class Event:
    __slots__ = ('id', 'tags', 'data', 'created_at', 'created_at_turn')

    def __init__(self, id, tags, data, created_at, created_at_turn):
        self.id = id
        self.tags = tags
        self.data = data
        self.created_at = created_at
        self.created_at_turn = created_at_turn

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.tags == other.tags and
                self.data == other.data and
                self.created_at == other.created_at and
                self.created_at_turn == other.created_at_turn)

    def __ne__(self, other):
        return not self.__eq__(other)
