# coding: utf-8
import random

from the_tale.game.prototypes import TimePrototype

from . import effects


class Job(object):
    __slots__ = ('name', 'created_at_turn', 'effect', 'positive_power', 'negative_power', 'power_required')
    ACTOR = None

    def __init__(self, name, created_at_turn, effect, positive_power, negative_power, power_required):
        self.name = name
        self.created_at_turn = created_at_turn
        self.effect = effect
        self.positive_power = positive_power
        self.negative_power = negative_power
        self.power_required = power_required

    @classmethod
    def create(cls, normal_power):
        effect =  random.choice([effect for effect in effects.EFFECT.records if effect.group.is_ON_HEROES])

        return cls(name=cls.create_name(effect),
                   created_at_turn=TimePrototype.get_current_turn_number(),
                   effect=effect,
                   positive_power=0,
                   negative_power=0,
                   power_required=normal_power * effect.power_modifier)

    def new_job(self, effect, normal_power):
        self.positive_power -= self.power_required
        self.negative_power -= self.power_required

        if self.positive_power < 0:
            self.positive_power = 0

        if self.negative_power < 0:
            self.negative_power = 0

        self.name = self.create_name(effect)
        self.created_at_turn = TimePrototype.get_current_turn_number()
        self.effect = effect
        self.power_required = normal_power * effect.power_modifier


    @classmethod
    def create_name(cls, effect):
        from the_tale.linguistics.logic import get_text

        return get_text(u'job_name_{actor}_{effect}'.format(actor=cls.ACTOR, effect=effect.name).upper(), {})


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


    def is_completed(self):
        return (self.positive_power >= self.power_required or
                self.negative_power >= self.power_required)


    def get_apply_effect_method(self):

        if self.positive_power > self.negative_power and self.positive_power >= self.power_required:
            return self.effect.logic.apply_positive

        if self.negative_power > self.positive_power and self.negative_power >= self.power_required:
            return self.effect.logic.apply_negative

        return None
