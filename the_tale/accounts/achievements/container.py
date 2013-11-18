# coding: utf-8

import time


class AchievementsContainer(object):

    __slots__ = ('updated', 'achievements')

    def __init__(self, achievements=None):
        self.updated = False
        self.achievements = achievements if achievements else {}

    def serialize(self):
        return {'achievements': self.achievements.items()}

    @classmethod
    def deserialize(cls, prototype, data):
        obj = cls()
        obj.achievements = dict(data.get('achievements', ()))
        return obj

    def add_achievement(self, achievement):

        if achievement.id in self.achievements:
            return

        self.updated = True
        self.achievements[achievement.id] = time.time()


    def remove_achievement(self, achievement):

        if achievement.id not in self.achievements:
            return

        self.updated = True
        del self.achievements[achievement.id]


    def has_achievement(self, achievement):
        return achievement.id in self.achievements

    def timestamp_for(self, achievement):
        return self.achievements.get(achievement.id)

    def achievements_ids(self): return self.achievements.iterkeys()

    def __len__(self):
         return len(self.achievements)

    def get_points(self):
        from the_tale.accounts.achievements.storage import achievements_storage
        return sum(achievements_storage[achievement_id].points for achievement_id in self.achievements.keys())

    def last_achievements(self, number):
        from the_tale.accounts.achievements.storage import achievements_storage
        achievements_ids = zip(*sorted((achievement_time, achievement_id)
                                       for achievement_id, achievement_time in self.achievements.iteritems())[:number])
        if achievements_ids:
            achievements_ids = achievements_ids[1]

        return [achievements_storage[achievement_id] for achievement_id in achievements_ids]
