# coding: utf-8

from the_tale.game.prototypes import TimePrototype

from . import effects


class Job(object):
    __slots__ = ('name', 'created_at_turn', 'effect', 'positive_power', 'negative_power', 'power_required')

    def __init__(self, name, created_at_turn, effect, positive_power, negative_power, power_required):
        self.name = name
        self.created_at_turn = created_at_turn
        self.effect = effect
        self.positive_power = positive_power
        self.negative_power = negative_power
        self.power_required = power_required

    @classmethod
    def create(cls):
        return cls(name='x',
                   created_at_turn=TimePrototype.get_current_turn_number(),
                   effect=effects.EFFECT.random(),
                   positive_power=0,
                   negative_power=0,
                   power_required=100)

    def new_job(self, owner):
        self.name = 'x'
        self.created_at_turn = TimePrototype.get_current_turn_number()
        self.effect = effects.EFFECT.random()
        self.positive_power = 0
        self.negative_power = 0
        self.power_required = 100


    def serialize(self):
        return {'name': self.name,
                'created_at_turn': self.created_at_turn,
                'effect': self.effect.value,
                'positive_power': self.positive_power,
                'negative_power': self.negative_power,
                'power_required': self.power_required}

    @classmethod
    def deserialize(cls, data):
        return cls(name=data['name'],
                   created_at_turn=data['created_at_turn'],
                   effect=effects.EFFECT(data['effect']),
                   positive_power=data['positive_power'],
                   negative_power=data['negative_power'],
                   power_required=data['power_required'])

    def give_power(self, power):
        if power > 0:
            self.positive_power += power
        else:
            self.negative_power -= power

        if self.positive_power > self.power_required:
            return self.effect.logic.apply_positive

        if -self.negative_power > self.power_required:
            return self.effect.logic.apply_negative

        return False
