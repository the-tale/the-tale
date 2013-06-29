# coding: utf-8

from dext.views import handler

from textgen.logic import Args

from common.utils.resources import Resource

from game.balance.enums import RACE_MULTIPLE_VERBOSE

from game.heroes.prototypes import HeroPrototype

from game.chronicle import RecordPrototype

from game.map.storage import map_info_storage
from game.map.places.storage import places_storage, buildings_storage, resource_exchange_storage
from game.map.places.prototypes import PlaceParametersDescription
from game.map.conf import map_settings
from game.map.relations import TERRAIN

class MapResource(Resource):

    def initialize(self, *args, **kwargs):
        super(MapResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.template('map/index.html')

    @handler('cell-info', method='get')
    def cell_info(self, x, y):

        x = int(x)
        y = int(y)

        if x < 0 or y < 0 or x >= map_settings.WIDTH or y >= map_settings.HEIGHT:
            return self.auto_error('game.map.cell_info.outside_map', u'Запрашиваемая зона не принадлежит карте')

        map_info = map_info_storage.item

        terrain = TERRAIN._ID_TO_TEXT[map_info.terrain[y][x]]

        cell = map_info.cells.get_cell(x, y)

        nearest_place_name = map_info.get_dominant_place(x, y).normalized_name.get_form(Args(u'рд'))

        place = places_storage.get_by_coordinates(x, y)

        dominant_race = None
        place_modifiers = None

        chronicle_records = []
        exchanges = []

        if place is not None:

            dominant_race = RACE_MULTIPLE_VERBOSE[place.race.value]

            place_modifiers = place.modifiers

            chronicle_records = RecordPrototype.get_last_actor_records(place, map_settings.CHRONICLE_RECORDS_NUMBER)

            for exchange in resource_exchange_storage.get_exchanges_for_place(place):
                resource_1, resource_2, place_2 = exchange.get_resources_for_place(place)
                exchanges.append((resource_1, resource_2, place_2, exchange.bill))


        terrain_points = []

        building = buildings_storage.get_by_coordinates(x, y)


        return self.template('map/cell_info.html',
                             {'place': place,
                              'building': building,
                              'place_modifiers': place_modifiers,
                              'exchanges': exchanges,
                              'cell': cell,
                              'terrain': terrain,
                              'nearest_place_name': nearest_place_name,
                              'dominant_race': dominant_race,
                              'PlaceParametersDescription': PlaceParametersDescription,
                              'x': x,
                              'y': y,
                              'terrain_points': terrain_points,
                              'chronicle_records': chronicle_records,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account.is_authenticated() else None} )
