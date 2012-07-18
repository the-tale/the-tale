# coding: utf-8
import random

from common.utils.storage import create_storage_class

from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype
from game.map.places.exceptions import PlacesException


class PlacesStorage(create_storage_class('places change time', Place, PlacePrototype, PlacesException)):

    def random_place(self):
        self.sync()

        return random.choice(self._data.values())


places_storage = PlacesStorage()
