
import smart_imports

smart_imports.all()


class AchievementsContainer(object):

    __slots__ = ('updated', 'achievements')

    def __init__(self, achievements=None):
        self.updated = False
        self.achievements = achievements if achievements else {}

    def serialize(self):
        return {'achievements': list(self.achievements.items())}

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

    def achievements_ids(self): return self.achievements.keys()

    def __len__(self):
        return len(self.achievements)

    def get_points(self):
        return sum(storage.achievements[achievement_id].points for achievement_id in self.achievements.keys())

    def last_achievements(self, number):
        achievements_ids = list(zip(*sorted((-achievement_time, achievement_id)
                                            for achievement_id, achievement_time in self.achievements.items())))
        if achievements_ids:
            achievements_ids = achievements_ids[1]

        return [storage.achievements[achievement_id]
                for achievement_id in achievements_ids
                if storage.achievements[achievement_id].approved][:number]
