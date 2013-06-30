# coding: utf-8
import random

from common.utils.storage import create_storage_class

from game.map.places.prototypes import PlacePrototype, BuildingPrototype, ResourceExchangePrototype
from game.map.places.exceptions import PlacesException
from game.map.places.relations import BUILDING_STATE


class PlacesStorage(create_storage_class('places change time', PlacePrototype._model_class, PlacePrototype, PlacesException)):

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

    def shift_all(self, dx, dy):
        for place in self.all():
            place.shift(dx, dy)
        self.save_all()


places_storage = PlacesStorage()


class BuildingsStorage(create_storage_class('buildings change time', BuildingPrototype._model_class, BuildingPrototype, PlacesException)):

    def _get_all_query(self): return BuildingPrototype._model_class.objects.exclude(state=BUILDING_STATE.DESTROYED)

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

    def shift_all(self, dx, dy):
        for building in self.all():
            building.shift(dx, dy)
        self.save_all()


buildings_storage = BuildingsStorage()


class ResourceExchangeStorage(create_storage_class('resource exchange change time', ResourceExchangePrototype._model_class, ResourceExchangePrototype, PlacesException)):

    def get_exchanges_for_place(self, place):
        exchanges = []
        for exchange in self.all():
            if place.id in (exchange.place_1.id, exchange.place_2.id):
                exchanges.append(exchange)
        return exchanges

    def get_exchange_for_bill_id(self, bill_id):
        for exchange in self.all():
            if exchange.bill_id == bill_id:
                return exchange
        return None


resource_exchange_storage = ResourceExchangeStorage()
