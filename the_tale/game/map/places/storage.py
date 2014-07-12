# coding: utf-8
import random

from the_tale.common.utils import storage

from the_tale.game.map.places.prototypes import PlacePrototype, BuildingPrototype, ResourceExchangePrototype
from the_tale.game.map.places import exceptions
from the_tale.game.map.places.relations import BUILDING_STATE


class PlacesStorage(storage.Storage):
    SETTINGS_KEY = 'places change time'
    EXCEPTION = exceptions.PlacesStorageError
    PROTOTYPE = PlacePrototype

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


class BuildingsStorage(storage.CachedStorage):
    SETTINGS_KEY = 'buildings change time'
    EXCEPTION = exceptions.BuildingsStorageError
    PROTOTYPE = BuildingPrototype

    def _get_all_query(self): return self.PROTOTYPE._model_class.objects.exclude(state=BUILDING_STATE.DESTROYED)

    def _reset_cache(self):
        self._persons_to_buildings = {}

    def _update_cached_data(self, item):
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


class ResourceExchangeStorage(storage.Storage):
    SETTINGS_KEY = 'resource exchange change time'
    EXCEPTION = exceptions.ResourceExchangeStorageError
    PROTOTYPE = ResourceExchangePrototype

    def get_exchanges_for_place(self, place):
        exchanges = []
        for exchange in self.all():
            if place.id in (exchange.place_1.id if exchange.place_1 is not None else None,
                            exchange.place_2.id if exchange.place_2 is not None else None):
                exchanges.append(exchange)
        return exchanges

    def get_exchange_for_bill_id(self, bill_id):
        for exchange in self.all():
            if exchange.bill_id == bill_id:
                return exchange
        return None


resource_exchange_storage = ResourceExchangeStorage()
