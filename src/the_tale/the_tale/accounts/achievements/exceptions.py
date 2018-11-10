
import smart_imports

smart_imports.all()


class AchievementsError(utils_exceptions.TheTaleError):
    MSG = 'achievements error'


class AchievementsManagerError(AchievementsError):
    MSG = 'achievements manager error'


class SaveNotRegisteredAchievementError(AchievementsError):
    MSG = 'try to save achievement %(achievement)r not from storage'
