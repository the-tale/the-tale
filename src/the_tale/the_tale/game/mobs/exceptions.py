# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class MobsError(TheTaleError):
    MSG = 'mobs error'

class MobsStorageError(MobsError):
    MSG = 'mobs storage error: %(message)s'

class SaveNotRegisteredMobError(MobsError):
    MSG = 'try to save mob %(mob)r not from storage'
