

class InnerCircle:
    __slots__ = ('rating',
                 'powers',
                 'size',
                 'circle',
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

        circle_rating = self.rating[:self.size]

        self.circle = frozenset(hero_id for hero_id, power in circle_rating)

        self.circle_positive_heroes_number = sum(1 if power > 0 else 0 for hero_id, power in circle_rating)
        self.circle_negative_heroes_number = sum(1 if power < 0 else 0 for hero_id, power in circle_rating)

        self.total_positive_heroes_number = sum(1 if power > 0 else 0 for hero_id, power in self.rating)
        self.total_negative_heroes_number = sum(1 if power < 0 else 0 for hero_id, power in self.rating)

    def get_positive_heroes_ids(self):
        return {hero_id for hero_id in self.circle if self.powers[hero_id] > 0}

    def get_negative_heroes_ids(self):
        return {hero_id for hero_id in self.circle if self.powers[hero_id] < 0}

    def in_circle(self, hero_id):
        return hero_id in self.circle

    def heroes_ids(self):
        return [hero_id for hero_id, amount in self.rating]

    def ui_info(self):
        return {'size': self.size,
                'rating': self.rating}
