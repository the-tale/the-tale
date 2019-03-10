
import smart_imports

smart_imports.all()


class RoadsStorage(utils_storage.Storage):
    SETTINGS_KEY = 'roads change time'
    EXCEPTION = exceptions.RoadsStorageError

    def _construct_object(self, model):
        from . import logic
        return logic.load_road(road_model=model)

    def _get_all_query(self):
        return models.Road.objects.all()


roads = RoadsStorage()
