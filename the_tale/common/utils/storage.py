# coding: utf-8

from dext.utils import storage


class Storage(storage.Storage):
    SETTINGS_KEY = None
    EXCEPTION = None
    PROTOTYPE = None

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _get_all_query(self): return self.PROTOTYPE._db_all()


class CachedStorage(storage.CachedStorage):
    SETTINGS_KEY = None
    EXCEPTION = None
    PROTOTYPE = None

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _get_all_query(self): return self.PROTOTYPE._db_all()


class SingleStorage(storage.SingleStorage):
    SETTINGS_KEY = None
    EXCEPTION = None
    PROTOTYPE = None

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)
