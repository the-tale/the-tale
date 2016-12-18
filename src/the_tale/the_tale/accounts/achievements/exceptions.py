# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class AchievementsError(TheTaleError):
    MSG = 'achievements error'


class AchievementsManagerError(AchievementsError):
    MSG = 'achievements manager error'


class SaveNotRegisteredAchievementError(AchievementsError):
    MSG = 'try to save achievement %(achievement)r not from storage'
