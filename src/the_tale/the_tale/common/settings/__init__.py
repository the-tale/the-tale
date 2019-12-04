

class Settings(object):

    def __init__(self):
        self.data = {}
        self.initialized = False

    def _load_data(self):
        from . import models
        return dict(models.Setting.objects.all().values_list('key', 'value'))

    def refresh(self, force=False):
        self.initialized = True
        self.data = self._load_data()

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise exceptions.WrongKeyType(key=key)

        if key not in self.data:
            raise exceptions.UnregisteredKey(key=key)

        if not self.initialized:
            self.refresh()

        return self.data[key]

    def __setitem__(self, key, value):
        import datetime

        from . import conf
        from . import models

        if not isinstance(key, str):
            raise exceptions.WrongKeyType(key=key)

        if not isinstance(value, str):
            raise exceptions.WrongValueType(value=value)

        if not self.initialized:
            self.refresh()

        if conf.settings.UPDATE_DATABASE:
            if key in self.data:
                models.Setting.objects.filter(key=key).update(value=value, updated_at=datetime.datetime.now())
            else:
                models.Setting.objects.create(key=key, value=value)

        self.data[key] = value

    def __delitem__(self, key):
        from . import models

        if not isinstance(key, str):
            raise exceptions.WrongKeyType(key=key)

        if not self.initialized:
            self.refresh()

        if key in self.data:
            models.Setting.objects.filter(key=key).delete()
        else:
            raise exceptions.KeyNotInSettings(key=key)

        del self.data[key]

    def __contains__(self, key):

        if not self.initialized:
            self.refresh()

        return key in self.data

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def clear(self):
        from . import models

        models.Setting.objects.all().delete()
        self.refresh()

    def records_number(self):
        from . import models

        return models.Setting.objects.all().count()


settings = Settings()
