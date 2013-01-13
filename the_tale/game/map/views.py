# coding: utf-8

from dext.views import handler

from textgen.logic import Args

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.prototypes import TimePrototype

from game.heroes.prototypes import HeroPrototype

from game.map.storage import map_info_storage
from game.map.logic import get_map_info
from game.map.places.prototypes import PlacePrototype
from game.map.generator import descriptors
from game.map.conf import map_settings
from game.map.places.models import TERRAIN

class MapResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(MapResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def info(self):
        map_info = get_map_info()
        return self.json(status='ok', data=map_info)

    @login_required
    @handler('cell-info', method='get')
    def cell_info(self, x, y):

        x = int(x)
        y = int(y)

        map_info = map_info_storage.item

        terrain = TERRAIN._ID_TO_TEXT[map_info.terrain[y][x]]

        world = map_info.world

        cell = world.cell_info(x, y)

        nearest_place_name = map_info.get_dominant_place(x, y).normalized_name[0].get_form(Args(u'дт'))

        randomized_cell = cell.randomize(seed=(x+y)*TimePrototype.get_current_time().game_time.day, fraction=map_settings.CELL_RANDOMIZE_FRACTION)

        place = PlacePrototype.get_by_coordinates(x, y)

        place_modifiers = place.modifiers if place else None

        return self.template('map/cell_info.html',
                             {'place': place,
                              'place_modifiers': place_modifiers,
                              'cell': cell,
                              'descr_wind': descriptors.wind(randomized_cell),
                              'descr_temperature': descriptors.temperature(randomized_cell),
                              'descr_wetness': descriptors.wetness(randomized_cell),
                              'terrain': terrain,
                              'nearest_place_name': nearest_place_name,
                              'x': x,
                              'y': y,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account else None} )
