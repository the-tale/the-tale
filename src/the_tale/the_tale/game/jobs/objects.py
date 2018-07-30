
import smart_imports

smart_imports.all()


class JobPower:
    __slots__ = ('positive', 'negative')

    def __init__(self, positive, negative):
        self.positive = positive
        self.negative = negative

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.positive == other.positive and
                self.negative == other.negative)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'JobPower({}, {})'.format(self.positive, self.negative)


class Job(object):
    __slots__ = ('name', 'created_at_turn', 'effect', 'power_required')

    ACTOR = NotImplemented
    ACTOR_TYPE = NotImplemented
    POSITIVE_TARGET_TYPE = NotImplemented
    NEGATIVE_TARGET_TYPE = NotImplemented
    NORMAL_POWER = NotImplemented

    def __init__(self, name, created_at_turn, effect, power_required):
        self.name = name
        self.created_at_turn = created_at_turn
        self.effect = effect
        self.power_required = power_required

    def serialize(self):
        return {'name': self.name,
                'created_at_turn': self.created_at_turn,
                'effect': self.effect.value,
                'power_required': self.power_required}

    @classmethod
    def deserialize(cls, data):
        return cls(name=data['name'],
                   created_at_turn=data['created_at_turn'],
                   effect=effects.EFFECT(data['effect']),
                   power_required=data['power_required'])

    def ui_info(self):
        return {'name': self.name,
                'effect': self.effect.value,
                'power_required': int(self.power_required)}

    def is_completed(self, job_power):
        return (job_power.positive >= self.power_required or
                job_power.negative >= self.power_required)

    def get_apply_effect_method(self, job_power):

        if job_power.positive > job_power.negative:
            return self.effect.logic.apply_positive

        return self.effect.logic.apply_negative

    def load_power(self, actor_id):
        raise NotImplementedError

    def load_inner_circle(self, actor_id):
        raise NotImplementedError

    def get_job_power(self, actor_id):
        raise NotImplementedError

    def get_project_name(self, actor_id):
        raise NotImplementedError

    def get_objects(self, actor_id):
        raise NotImplementedError

    def get_effects_priorities(self, actor_id):
        raise NotImplementedError

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.created_at_turn == other.created_at_turn and
                self.effect == other.effect and
                self.power_required == other.power_required)

    def __ne__(self, other):
        return not self.__eq__(other)
