# coding: utf-8


from the_tale.game.balance import constants as c



class PoliticPower(object):
    __slots__ = ('outer_power', 'inner_power', 'inner_circle', '_inner_positive_heroes', '_inner_negative_heroes')
    INNER_CIRCLE_SIZE = None

    def __init__(self, outer_power, inner_power, inner_circle):
        self.outer_power = outer_power
        self.inner_power = inner_power
        self.inner_circle = inner_circle

        self.reset_cache()


    @classmethod
    def create(cls):
        return cls(outer_power=0, inner_power=0, inner_circle={})

    def reset_cache(self):
        self._inner_positive_heroes = None
        self._inner_negative_heroes = None

    def serialize(self):
        return {'outer_power': self.outer_power,
                'inner_power': self.inner_power,
                'inner_circle': self.inner_circle}

    @classmethod
    def deserialize(cls, data):
        return cls(outer_power=data['outer_power'],
                   inner_power=data['inner_power'],
                   inner_circle=data['inner_circle'])


    def change_power(self, owner, hero_id, has_in_preferences, power):

        if hero_id is not None:
            if has_in_preferences:
                self.inner_circle[hero_id] = self.inner_circle.get(hero_id, 0) + power
                self.reset_cache()

            if not self.is_in_inner_circle(hero_id):
                self.outer_power += power
                return

        self.inner_power += power

        job_effect = owner.job.give_power(power)

        if job_effect:
            job_effect(**self.job_effect_kwargs(owner))
            owner.job.new_job(owner)


    def job_effect_kwargs(self, owner):
        raise NotImplementedError()


    def sync_power(self):
        remove_candidates = set()

        for hero_id, power in self.inner_circle.iteritems():
            new_power = power * c.PLACE_POWER_REDUCE_FRACTION
            self.inner_circle[hero_id] = new_power

            if abs(new_power) < 0.001:
                remove_candidates.add(hero_id)

        for hero_id in remove_candidates:
            del self.inner_circle[hero_id]

        self.reset_cache()


    def is_in_inner_circle(self, hero_id):

        if self._inner_positive_heroes is None:
            self.update_inner_heroes()

        return hero_id in self._inner_positive_heroes or hero_id in self._inner_negative_heroes


    # TODO: can be optimized by used memory
    def update_inner_heroes(self):
        positive_heroes = []
        negative_heroes = []

        for hero_id, power in self.inner_circle.iteritems():
            if power > 0:
                positive_heroes.append((power, hero_id))
            else:
                negative_heroes.append((-power, hero_id))

        positive_heroes.sort()
        negative_heroes.sort()

        self._inner_positive_heroes = frozenset((hero_id for power, hero_id in positive_heroes))
        self._inner_negative_heroes = frozenset((hero_id for power, hero_id in negative_heroes))
