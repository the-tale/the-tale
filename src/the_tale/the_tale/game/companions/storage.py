
import smart_imports

smart_imports.all()


class CompanionsStorage(utils_storage.Storage):
    SETTINGS_KEY = 'companions-storage'
    EXCEPTION = exceptions.CompanionsStorageError

    def _construct_object(self, model):
        return objects.CompanionRecord.from_model(model)

    def _get_all_query(self):
        return models.CompanionRecord.objects.all()

    def enabled_companions(self):
        return (companion for companion in self.all() if companion.state.is_ENABLED)


companions = CompanionsStorage()
