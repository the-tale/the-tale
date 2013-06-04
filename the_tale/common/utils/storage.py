# coding: utf-8
import uuid
import contextlib
import functools

from dext.settings import settings

def create_storage_class(version_key, Model, Prototype, Exception_): # pylint: disable=R0912

    class Storage(object):

        SETTINGS_KEY = version_key

        def __init__(self):
            self.clear()
            self._postpone_version_update_nesting = 0
            self._update_version_requested = False

        @property
        def version(self):
            self.sync()
            return self._version

        def _get_all_query(self): return Model.objects.all()

        def refresh(self):
            self.clear()

            self._version = settings[self.SETTINGS_KEY]

            for model in self._get_all_query():
                self.add_item(model.id, Prototype(model))

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
            self._version = None
            self._update_version_requested = False

        def save_all(self):
            with self.postpone_version_update():
                for record in self._data.values():
                    record.save()

        def _setup_version(self):
            self._version = uuid.uuid4().hex
            settings[self.SETTINGS_KEY] = str(self._version)
            self._update_version_requested = False

        def update_version(self):
            self._update_version_requested = True

            if self._postpone_version_update_nesting > 0:
                return

            self._setup_version()

        @contextlib.contextmanager
        def _postpone_version_update(self):
            self._postpone_version_update_nesting += 1

            yield

            self._postpone_version_update_nesting -= 1

            if self._update_version_requested:
                self.update_version()

        def postpone_version_update(self, func=None):

            if func is None:
                return self._postpone_version_update()

            @functools.wraps(func)
            def wrapper(*argv, **kwargs):
                with self._postpone_version_update():
                    return func(*argv, **kwargs)

            return wrapper


    return Storage


def create_single_storage_class(version_key, Model, Prototype, Exception_): # pylint: disable=R0912,W0613

    class SingleStorage(object):

        SETTINGS_KEY = version_key

        def __init__(self):
            self.clear()

        @property
        def version(self):
            self.sync()
            return self._version

        def refresh(self):
            raise NotImplementedError

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

        @property
        def item(self):
            self.sync()
            return self._item

        def set_item(self, item):
            self._item = item
            self.update_version()

        def clear(self):
            self._item = None
            self._version = None

        def _setup_version(self):
            self._version = uuid.uuid4().hex
            settings[self.SETTINGS_KEY] = str(self._version)

        def update_version(self):
            self._setup_version()


    return SingleStorage
