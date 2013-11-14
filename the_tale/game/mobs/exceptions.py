# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class MobsError(TheTaleError):
    MSG = u'mobs error'

class MobsStorageError(MobsError):
    MSG = u'mobs storage error'

class SaveNotRegisteredMobError(MobsError):
    MSG = u'try to save mob %(mob)r not from storage'
