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

        self.achievements[achievement.id] = time.time()

    def has_achievement(self, achievement):
        return achievement.id in self.achievements
