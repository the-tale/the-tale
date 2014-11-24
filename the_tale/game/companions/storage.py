# coding: utf-8

from dext.common.utils import storage

from the_tale.game.companions import exceptions
from the_tale.game.companions import objects
from the_tale.game.companions import models


class CompanionsStorage(storage.Storage):
    SETTINGS_KEY = 'companions-storage'
    EXCEPTION = exceptions.CompanionsStorageError

    def _construct_object(self, model):
        return objects.CompanionRecord.from_model(model)

    def _get_all_query(self):
        return models.CompanionRecord.objects.all()


companions_storage = CompanionsStorage()
