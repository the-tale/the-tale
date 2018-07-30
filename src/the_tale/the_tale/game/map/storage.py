
import smart_imports

smart_imports.all()


class MapInfoStorage(utils_storage.SingleStorage):
    SETTINGS_KEY = 'map info change time'
    EXCEPTION = exceptions.MapStorageError
    PROTOTYPE = prototypes.MapInfoPrototype

    def _construct_zero_item(self):
        return None

    def refresh(self):
        self.clear()

        try:
            self._item = prototypes.MapInfoPrototype(prototypes.MapInfoPrototype._model_class.objects.order_by('-turn_number', '-id')[0])
        except IndexError:
            self._item = None

        self._version = dext_settings.settings[self.SETTINGS_KEY]

    def _get_next_version(self):
        return '%d-%f' % (game_turn.number(), time.time())


map_info = MapInfoStorage()
