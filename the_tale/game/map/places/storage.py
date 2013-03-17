# coding: utf-8
import random

from common.utils.storage import create_storage_class

from game.map.places.models import Place, Building
from game.map.places.prototypes import PlacePrototype, BuildingPrototype
from game.map.places.exceptions import PlacesException
from game.map.places.relations import BUILDING_STATE


class PlacesStorage(create_storage_class('places change time', Place, PlacePrototype, PlacesException)):

    def random_place(self):
        self.sync()
        return random.choice(self._data.values())

    def get_choices(self):
        self.sync()
        return [(place.id, place.name) for place in sorted(self.all(), key=lambda p: p.name)]

    def get_by_coordinates(self, x, y):
        self.sync()
        for place in self.all():
            if place.x == x and place.y == y:
                return place

        return None


places_storage = PlacesStorage()


class BuildingsStorage(create_storage_class('buildings change time', Building, BuildingPrototype, PlacesException)):

    def _get_all_query(self): return Building.objects.exclude(state=BUILDING_STATE.DESTROED)

    def __init__(self, *argv, **kwargs):
        self._persons_to_buildings = {}
        super(BuildingsStorage, self).__init__(*argv, **kwargs)

    def clear(self):
        self._persons_to_buildings = {}
        super(BuildingsStorage, self).clear()

    def add_item(self, id_, item):
        super(BuildingsStorage, self).add_item(id_=id_, item=item)
        self._persons_to_buildings[item.person.id] = item

    def get_by_person_id(self, person_id):
        self.sync()
        return self._persons_to_buildings.get(person_id)

    def get_by_coordinates(self, x, y):
        self.sync()
        for building in self.all():
            if building.x == x and building.y == y:
                return building

        return None



buildings_storage = BuildingsStorage()
