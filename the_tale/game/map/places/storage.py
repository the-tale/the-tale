# coding: utf-8
import random

from common.utils.storage import create_storage_class

from game.map.places.models import Place, Building
from game.map.places.prototypes import PlacePrototype, BuildingPrototype
from game.map.places.exceptions import PlacesException


class PlacesStorage(create_storage_class('places change time', Place, PlacePrototype, PlacesException)):

    def random_place(self):
        self.sync()
        return random.choice(self._data.values())

    def get_choices(self):
        self.sync()
        return [(place.id, place.name) for place in sorted(self.all(), key=lambda p: p.name)]


places_storage = PlacesStorage()


class BuildingsStorage(create_storage_class('buildings change time', Building, BuildingPrototype, PlacesException)):

    def __init__(self, *argv, **kwargs):
        self.persons_to_buildings = {}
        super(BuildingsStorage, self).__init__(*argv, **kwargs)

    def clear(self):
        self.persons_to_buildings = {}
        super(BuildingsStorage, self).clear()

    def add_item(self, id_, item):
        super(BuildingsStorage, self).add_item(id_=id_, item=item)
        self.persons_to_buildings[item.person.id] = item


buildings_storage = BuildingsStorage()
