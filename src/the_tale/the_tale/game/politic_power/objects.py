

class InnerCircle:
    __slots__ = ('rating',
                 'powers',
                 'size',
                 'positive_heroes',
                 'negative_heroes',
                 'total_positive_heroes_number',
                 'total_negative_heroes_number',
                 'circle_positive_heroes_number',
                 'circle_negative_heroes_number')

    def __init__(self, rating, size):
        self.size = size
        self.rating = rating

        self.rating.sort(key=lambda item: (abs(item[1]),
                                           1 if item[1] > 0 else -1,
                                           item[0]),
                         reverse=True)

        self.powers = dict(self.rating)

        positive_heroes = []
        negative_heroes = []

        for hero_id, power in self.rating:
            if power > 0:
                positive_heroes.append((power, hero_id))
            elif power < 0:
                negative_heroes.append((-power, hero_id))

        positive_heroes.sort()
        negative_heroes.sort()

        self.total_positive_heroes_number = len(positive_heroes)
        self.total_negative_heroes_number = len(negative_heroes)

        self.positive_heroes = frozenset((hero_id for power, hero_id in positive_heroes[-self.size:]))
        self.negative_heroes = frozenset((hero_id for power, hero_id in negative_heroes[-self.size:]))

        self.circle_positive_heroes_number = len(self.positive_heroes)
        self.circle_negative_heroes_number = len(self.negative_heroes)

    def in_circle(self, hero_id):
        return hero_id in self.positive_heroes or hero_id in self.negative_heroes

    def heroes_ids(self):
        return [hero_id for hero_id, amount in self.rating]

    def ui_info(self):
        return {'positive': {hero_id: self.powers[hero_id] for hero_id in self.positive_heroes},
                'negative': {hero_id: self.powers[hero_id] for hero_id in self.negative_heroes}}
