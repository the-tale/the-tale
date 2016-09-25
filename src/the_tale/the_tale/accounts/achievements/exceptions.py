# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class AchievementsError(TheTaleError):
    MSG = u'achievements error'


class AchievementsManagerError(AchievementsError):
    MSG = u'achievements manager error'


class SaveNotRegisteredAchievementError(AchievementsError):
    MSG = u'try to save achievement %(achievement)r not from storage'
