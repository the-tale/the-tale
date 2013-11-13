# coding: utf-8


from the_tale.common.utils.storage import create_storage_class

from the_tale.accounts.achievements.prototypes import AchievementPrototype
from the_tale.accounts.achievements.exceptions import AchievementsError


class AchievementsStorage(create_storage_class('achievements change time', AchievementPrototype, AchievementsError)):

    def by_group(self, group, only_approved):
        by_group =  (achievement for achievement in self.all() if achievement.group == group)

        if only_approved:
            by_group = (achievement for achievement in by_group if  achievement.approved)

        return by_group


achievements_storage = AchievementsStorage()
