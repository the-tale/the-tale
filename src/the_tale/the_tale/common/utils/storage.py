
import smart_imports

smart_imports.all()


class BaseStorage(object):
    __slots__ = ('_postpone_version_update_nesting', '_update_version_requested', '_version')

    SETTINGS_KEY = NotImplemented
    EXCEPTION = NotImplemented

    def _construct_object(self, model):
        raise NotImplementedError()

    def refresh(self):
        raise NotImplementedError()

    def __init__(self):
        self.clear()
        self._postpone_version_update_nesting = 0
        self._update_version_requested = False

    @property
    def version(self):
        self.sync()
        return self._version

    def sync(self, force=False):
        if self._version != global_settings.get(self.SETTINGS_KEY):
            self.refresh()
            return

        if force:
            self.refresh()
            return

    def _get_next_version(self):
        return uuid.uuid4().hex

    def _setup_version(self):
        self._version = self._get_next_version()
        global_settings[self.SETTINGS_KEY] = str(self._version)
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


class Storage(BaseStorage):
    __slots__ = ('data', )

    def _get_all_query(self):
        raise NotImplementedError()

    def refresh(self):
        self.clear()

        self._version = global_settings.get(self.SETTINGS_KEY)

        for model in self._get_all_query():
            item = self._construct_object(model)
            self.add_item(item.id, item)

    def __getitem__(self, id_):
        self.sync()

        if id_ not in self._data:
            raise self.EXCEPTION(message='no object with id: %s' % id_)

        return self._data[id_]

    def add_item(self, id_, item):
        self.sync()
        self._data[id_] = item

    def remove_item(self, id_):
        self.sync()

        if id_ in self._data:
            del self._data[id_]
            return True

        return False

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

        return list(self._data.values())

    def __len__(self):
        self.sync()
        return len(self._data)

    def is_empty(self):
        self.sync()
        return bool(self._data)

    def clear(self):
        self._data = {}
        self._version = None
        self._update_version_requested = False

    def save_all(self):
        with self.postpone_version_update():
            for record in list(self._data.values()):
                self._save_object(record)


class CachedStorage(Storage):
    __slots__ = ()

    def _reset_cache(self):
        raise NotImplementedError()

    def _update_cached_data(self, item):
        raise NotImplementedError()

    def add_item(self, id_, item):
        super(CachedStorage, self).add_item(id_, item)
        self._update_cached_data(item)

    def remove_item(self, id_):
        if not super().remove_item(id_):
            return False

        self._reset_cache()

        for item in self.all():
            self._update_cached_data(item)

        return True

    def refresh(self):
        self._reset_cache()
        super(CachedStorage, self).refresh()

    def clear(self):
        self._reset_cache()
        super(CachedStorage, self).clear()


class SingleStorage(BaseStorage):
    __slots__ = ('_item',)

    @property
    def item(self):
        self.sync()
        return self._item

    def set_item(self, item):
        self._item = item
        self.update_version()

    def _construct_zero_item(self):
        raise NotImplementedError()

    def clear(self):
        self._item = self._construct_zero_item()
        self._version = None
        self._update_version_requested = False


class DependentStorage:
    __slots__ = ('_version', )

    def __init__(self):
        self.reset_version()

    def reset(self):
        self.reset_version()

    def reset_version(self):
        self._version = uuid.uuid4().hex

    def sync(self, force=False):

        if not force and not self.is_changed():
            return

        self.reset()

        self.recalculate()

        self.actualize_version()

    def actualize_version(self):
        self._version = self.expected_version()

    def is_changed(self):
        return self._version != self.expected_version()

    def recalculate(self):
        raise NotImplementedError

    def expected_version(self):
        raise NotImplementedError


class PrototypeStorage(Storage):
    PROTOTYPE = NotImplemented

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _save_object(self, obj):
        obj.save()

    def _get_all_query(self):
        return self.PROTOTYPE._db_all()


class CachedPrototypeStorage(CachedStorage):
    PROTOTYPE = NotImplemented

    def _construct_object(self, model):
        return self.PROTOTYPE(model=model)

    def _save_object(self, obj):
        obj.save()

    def _get_all_query(self):
        return self.PROTOTYPE._db_all()
