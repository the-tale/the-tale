# coding: utf-8


from the_tale.game.balance import constants as c



class PoliticPower(object):
    __slots__ = ('outer_power', 'inner_power', 'inner_circle', '_inner_positive_heroes', '_inner_negative_heroes')
    INNER_CIRCLE_SIZE = None
    POWER_REMOVE_BARRIER = 1

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

    @property
    def inner_positive_heroes(self):
        if self._inner_positive_heroes is None:
            self.update_inner_heroes()

        return self._inner_positive_heroes

    @property
    def inner_negative_heroes(self):
        if self._inner_negative_heroes is None:
            self.update_inner_heroes()

        return self._inner_negative_heroes

    @property
    def positive_heroes_number(self):
        return len([power for power in self.inner_circle.itervalues() if power > 0 ])

    @property
    def negative_heroes_number(self):
        return len([power for power in self.inner_circle.itervalues() if power < 0 ])

    def serialize(self):
        return {'outer_power': self.outer_power,
                'inner_power': self.inner_power,
                'inner_circle': self.inner_circle}

    @classmethod
    def deserialize(cls, data):
        return cls(outer_power=data['outer_power'],
                   inner_power=data['inner_power'],
                   inner_circle={int(account_id): power for account_id, power in data['inner_circle'].iteritems()})

    def ui_info(self, all_powers):
        return {'power': {'inner': {'value': self.inner_power,
                                    'fraction': self.inner_power_fraction(all_powers)},
                          'outer': {'value': self.outer_power,
                                    'fraction': self.outer_power_fraction(all_powers)},
                          'fraction': self.total_politic_power_fraction(all_powers)},
                'heroes': {'positive': {hero_id: self.inner_circle[hero_id] for hero_id in self.inner_positive_heroes},
                           'negative': {hero_id: self.inner_circle[hero_id] for hero_id in self.inner_negative_heroes}}}

    def inner_accounts_ids(self):
        return self.inner_circle.iterkeys()

    def inner_circle_rating(self):
        return sorted(self.inner_circle.iteritems(), key=lambda x: abs(x[1]), reverse=True)

    def change_power(self, owner, hero_id, has_in_preferences, power):

        if hero_id is None:
            self.outer_power += power
            return

        if has_in_preferences:
            self.inner_circle[hero_id] = self.inner_circle.get(hero_id, 0) + power
            self.reset_cache()

        if not self.is_in_inner_circle(hero_id):
            self.outer_power += power
            return

        self.inner_power += power

        owner.job.give_power(power)


    def job_effect_kwargs(self, owner):
        raise NotImplementedError()


    def sync_power(self):
        remove_candidates = set()

        for hero_id, power in self.inner_circle.iteritems():
            new_power = power * c.PLACE_POWER_REDUCE_FRACTION
            self.inner_circle[hero_id] = new_power

            if abs(new_power) <= self.POWER_REMOVE_BARRIER:
                remove_candidates.add(hero_id)

        for hero_id in remove_candidates:
            del self.inner_circle[hero_id]

        self.inner_power *= c.PLACE_POWER_REDUCE_FRACTION
        self.outer_power *= c.PLACE_POWER_REDUCE_FRACTION

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

        self._inner_positive_heroes = frozenset((hero_id for power, hero_id in positive_heroes[-self.INNER_CIRCLE_SIZE:]))
        self._inner_negative_heroes = frozenset((hero_id for power, hero_id in negative_heroes[-self.INNER_CIRCLE_SIZE:]))

    def inner_power_fraction(self, all_powers):
        # находим минимальное отрицательное влияние и компенсируем его при расчёте долей
        minimum_power = 0.0

        for obj in all_powers:
            minimum_power = min(minimum_power, obj.inner_power)

        total_power = 0.0

        for obj in all_powers:
            total_power += (obj.inner_power - minimum_power)

        return ((self.inner_power - minimum_power) / total_power) if total_power else 0

    def outer_power_fraction(self, all_powers):
        # находим минимальное отрицательное влияние и компенсируем его при расчёте долей
        minimum_power = 0.0

        for obj in all_powers:
            minimum_power = min(minimum_power, obj.outer_power)

        total_power = 0.0

        for obj in all_powers:
            total_power += (obj.outer_power - minimum_power)

        return ((self.outer_power - minimum_power) / total_power) if total_power else 0


    def total_politic_power_fraction(self, all_powers):
        return (self.inner_power_fraction(all_powers) + self.outer_power_fraction(all_powers)) / 2


    def __unicode__(self): return u'{}, {}'.format(self.outer_power, self.inner_power)
