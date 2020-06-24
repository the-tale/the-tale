
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
    __slots__ = ('name', 'created_at_turn', 'effect')

    ACTOR = NotImplemented
    ACTOR_TYPE = NotImplemented
    POSITIVE_TARGET_TYPE = NotImplemented
    NEGATIVE_TARGET_TYPE = NotImplemented
    NORMAL_POWER = NotImplemented

    def __init__(self, name, created_at_turn, effect):
        self.name = name
        self.created_at_turn = created_at_turn
        self.effect = effect

    @property
    def power_required(self):
        try:
            return self.effect.logic.power_required(self.NORMAL_POWER)
        except Exception as e:
            print(e)

    def serialize(self):
        return {'name': self.name,
                'created_at_turn': self.created_at_turn,
                'effect': self.effect.value}

    @classmethod
    def deserialize(cls, data):
        return cls(name=data['name'],
                   created_at_turn=data['created_at_turn'],
                   effect=effects.EFFECT(data['effect']))

    def ui_info(self, actor_id):
        power = self.load_power(actor_id)

        return {'name': self.name,
                'effect': self.effect.value,
                'positive_power': int(power.positive),
                'negative_power': int(power.negative),
                'power_required': int(self.power_required)}

    def can_be_completed_at_turn(self):
        return int(self.created_at_turn + c.JOB_MIN_LENGTH * 24 * c.TURNS_IN_HOUR)

    def will_be_completed_after(self):
        return datetime.timedelta(seconds=((self.can_be_completed_at_turn() - game_turn.number()) * c.TURN_DELTA))

    def is_completed(self, job_power):
        if game_turn.number() < self.can_be_completed_at_turn():
            return False

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
