
import smart_imports

smart_imports.all()


class MobsError(utils_exceptions.TheTaleError):
    MSG = 'mobs error'


class MobsStorageError(MobsError):
    MSG = 'mobs storage error: %(message)s'


class SaveNotRegisteredMobError(MobsError):
    MSG = 'try to save mob %(mob)r not from storage'


class NoWeaponsError(MobsError):
    MSG = 'mob %(mob_id)s MUST has at least one weapon'
