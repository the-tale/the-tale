
import smart_imports

smart_imports.all()


class InfosStorage(utils_storage.Storage):
    SETTINGS_KEY = 'clans infos change time'
    EXCEPTION = exceptions.ClansInfosStorageError

    def _construct_object(self, model):
        return objects.ClanInfo(id=model.id,
                                name=model.name,
                                linguistics_name=utg_words.Word.deserialize(model.data['linguistics_name']),
                                abbr=model.abbr,
                                motto=model.motto,
                                state=model.state)

    def _save_object(self, info):
        raise NotImplementedError

    def _get_all_query(self):
        return models.Clan.objects.all()


infos = InfosStorage()
