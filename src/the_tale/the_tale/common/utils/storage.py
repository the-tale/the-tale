
import smart_imports

smart_imports.all()


class Storage(dext_storage.Storage):
    SETTINGS_KEY = None
    EXCEPTION = None
    PROTOTYPE = None

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _save_object(self, obj):
        obj.save()

    def _get_all_query(self): return self.PROTOTYPE._db_all()


class CachedStorage(dext_storage.CachedStorage):
    SETTINGS_KEY = None
    EXCEPTION = None
    PROTOTYPE = None

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _save_object(self, obj):
        obj.save()

    def _get_all_query(self): return self.PROTOTYPE._db_all()


class SingleStorage(dext_storage.SingleStorage):
    SETTINGS_KEY = None
    EXCEPTION = None
