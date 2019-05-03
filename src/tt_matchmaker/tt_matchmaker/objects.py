

class BattleRequest:
    __slots__ = ('id', 'initiator_id', 'matchmaker_type', 'created_at', 'updated_at')

    def __init__(self, id, initiator_id, matchmaker_type, created_at, updated_at):
        self.id = id
        self.initiator_id = initiator_id
        self.matchmaker_type = matchmaker_type
        self.created_at = created_at
        self.updated_at = updated_at

    def __eq__(self, other):
        return (self.__class__ == other.__class and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)


class Battle:
    __slots__ = ('id', 'matchmaker_type', 'participants_ids', 'created_at')

    def __init__(self, id, matchmaker_type, participants_ids, created_at):
        self.id = id
        self.matchmaker_type = matchmaker_type
        self.participants_ids = participants_ids
        self.created_at = created_at

    def __eq__(self, other):
        return (self.__class__ == other.__class and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
