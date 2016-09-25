# coding: utf-8
import contextlib
import collections

from the_tale.common.utils import storage

from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.exceptions import AchievementsError
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP


class AchievementsStorage(storage.Storage):
    SETTINGS_KEY = 'achievements change time'
    EXCEPTION = AchievementsError
    PROTOTYPE = AchievementPrototype

    def by_group(self, group, only_approved):
        by_group =  (achievement for achievement in self.all() if achievement.group == group)

        if only_approved:
            by_group = (achievement for achievement in by_group if  achievement.approved)

        return by_group

    def by_type(self, type, only_approved):
        by_type =  (achievement for achievement in self.all() if achievement.type == type)

        if only_approved:
            by_type = (achievement for achievement in by_type if  achievement.approved)

        return by_type


    def verify_achievements(self, account_id, type, old_value, new_value):
        if old_value == new_value:
            return

        for achievement in self.by_type(type, only_approved=True):
            if achievement.check(old_value, new_value):
                AccountAchievementsPrototype.give_achievement(account_id=account_id, achievement=achievement)

    @contextlib.contextmanager
    def verify(self, type, object):
        old_value = object.get_achievement_type_value(type)
        yield
        self.verify_achievements(account_id=object.get_achievement_account_id(),
                                 type=type,
                                 old_value=old_value,
                                 new_value=object.get_achievement_type_value(type))


    def get_groups_statistics(self, account_achievements):
        groups_count = collections.Counter(achievement.group for achievement in self.all() if achievement.approved)

        if account_achievements:
            account_count = collections.Counter(self[achievement_id].group for achievement_id in account_achievements.achievements_ids() if self[achievement_id].approved )
        else:
            account_count = collections.Counter()

        statistics = {group: (account_count[group], groups_count[group]) for group in ACHIEVEMENT_GROUP.records}

        statistics[None] = (sum(account_count.values()), sum(groups_count.values()))

        return statistics



achievements_storage = AchievementsStorage()
