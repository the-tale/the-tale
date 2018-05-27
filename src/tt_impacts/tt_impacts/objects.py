

class Object:
    __slots__ = ('type', 'id')

    def __init__(self, type, id):
        self.type = type
        self.id = id

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.type == other.type and
                self.id == other.id)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type, self.id))

    def __repr__(self):
        return 'Object({}, {})'.format(self.type, self.id)


class Impact:
    __slots__ = ('transaction', 'actor', 'target', 'amount', 'turn', 'time')

    def __init__(self, transaction, actor, target, amount, turn, time):
        self.transaction = transaction
        self.actor = actor
        self.target = target
        self.amount = amount
        self.turn = turn
        self.time = time

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.transaction == other.transaction and
                self.actor == other.actor and
                self.target == other.target and
                self.amount == other.amount and
                self.turn == other.turn and
                self.time == other.time)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Impact: {} {} {} {} {} {}>'.format(self.transaction,
                                                    self.actor,
                                                    self.target,
                                                    self.amount,
                                                    self.turn,
                                                    self.time)


class ActorImpact:
    __slots__ = ('actor', 'target', 'amount', 'turn', 'time')

    def __init__(self, actor, target, amount, turn, time):
        self.actor = actor
        self.target = target
        self.amount = amount
        self.turn = turn
        self.time = time

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.actor == other.actor and
                self.target == other.target and
                self.amount == other.amount and
                self.turn == other.turn and
                self.time == other.time)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Impact: {} {} {} {} {}>'.format(self.actor,
                                                 self.target,
                                                 self.amount,
                                                 self.turn,
                                                 self.time)


class TargetImpact:
    __slots__ = ('target', 'amount', 'turn', 'time')

    def __init__(self, target, amount, turn, time):
        self.target = target
        self.amount = amount
        self.turn = turn
        self.time = time

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.target == other.target and
                self.amount == other.amount and
                self.turn == other.turn and
                self.time == other.time)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Impact: {} {} {} {}>'.format(self.target,
                                              self.amount,
                                              self.turn,
                                              self.time)
