# coding: utf-8
import time
import random

from dext.settings import settings

from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype
from game.map.places.exceptions import PlacesException


class PlacesStorage(object):

    SETTINGS_KEY = 'places change time'

    def __init__(self):
        self._places = {}
        self._version = -1

    def refresh(self):
        self._version = int(settings[self.SETTINGS_KEY])

        for place_model in Place.objects.all():
            self._places[place_model.id] = PlacePrototype(place_model)

    def sync(self, force=False):
        if self.SETTINGS_KEY not in settings:
            settings[self.SETTINGS_KEY] = '0'
            self.refresh()
            return

        if self._version < int(settings[self.SETTINGS_KEY]):
            self.refresh()
            return

        if force:
            self.refresh()
            return

    def __getitem__(self, id_):
        self.sync()

        if id_ not in self._places:
            raise PlacesException('wrong place id: %d' % id_)

        return self._places[id_]

    def __contains__(self, id_):
        self.sync()
        return id_ in self._places

    def get(self, id_, default=None):
        self.sync()

        if id_ in self._places:
            return self._places[id_]
        return default

    def all(self):
        self.sync()

        return self._places.values()

    def save_all(self):
        for place in self._places.values():
            place.save()

        self._version = int(time.time())
        settings[self.SETTINGS_KEY] = str(self._version)

    def random_place(self):
        self.sync()

        return random.choice(self._places.values())




places_storage = PlacesStorage()
