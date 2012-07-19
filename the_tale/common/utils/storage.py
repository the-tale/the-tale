# coding: utf-8
import uuid

from dext.settings import settings

def create_storage_class(version_key, Model, Prototype, Exception_):

    class Storage(object):

        SETTINGS_KEY = version_key

        def __init__(self):
            self.clear()

        def refresh(self):
            self._version = settings[self.SETTINGS_KEY]

            for model in Model.objects.all():
                self._data[model.id] = Prototype(model)

        def sync(self, force=False):
            if self.SETTINGS_KEY not in settings:
                self.update_version()
                self.refresh()
                return

            if self._version != settings[self.SETTINGS_KEY]:
                self.refresh()
                return

            if force:
                self.refresh()
                return

        def __getitem__(self, id_):
            self.sync()

            if id_ not in self._data:
                raise Exception_('wrong %r id: %s' % (Model, id_))

            return self._data[id_]

        def add_item(self, id_, item):
            '''
            only for add new items, not for any other sort of management
            '''
            self._data[id_] = item

        def __contains__(self, id_):
            self.sync()
            return id_ in self._data

        def get(self, id_, default=None):
            self.sync()

            if id_ in self._data:
                return self._data[id_]
            return default

        def all(self):
            self.sync()

            return self._data.values()

        def clear(self):
            self._data = {}
            self._version = -1

        def save_all(self):
            for road in self._data.values():
                road.save()

            self.update_version()

        def update_version(self):
            self._version = uuid.uuid4().hex
            settings[self.SETTINGS_KEY] = str(self._version)


    return Storage
