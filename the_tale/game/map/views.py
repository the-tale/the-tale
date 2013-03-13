# coding: utf-8

from dext.views import handler

from textgen.logic import Args

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.prototypes import TimePrototype

from game.balance.enums import RACE_MULTIPLE_VERBOSE

from game.heroes.prototypes import HeroPrototype

from game.chronicle import RecordPrototype

from game.map.storage import map_info_storage
from game.map.places.prototypes import PlacePrototype
from game.map.generator import descriptors
from game.map.generator.biomes import Biom
from game.map.conf import map_settings
from game.map.relations import TERRAIN

class MapResource(Resource):

    def initialize(self, *args, **kwargs):
        super(MapResource, self).initialize(*args, **kwargs)

    @login_required
    @handler('', method='get')
    def index(self):
        return self.template('map/index.html')

    @login_required
    @handler('cell-info', method='get')
    def cell_info(self, x, y):

        x = int(x)
        y = int(y)

        map_info = map_info_storage.item

        terrain = TERRAIN._ID_TO_TEXT[map_info.terrain[y][x]]

        world = map_info.world

        cell = world.cell_info(x, y)
        cell_power = world.cell_power_info(x, y)

        nearest_place_name = map_info.get_dominant_place(x, y).normalized_name.get_form(Args(u'рд'))

        randomized_cell = cell.randomize(seed=(x+y)*TimePrototype.get_current_time().game_time.day, fraction=map_settings.CELL_RANDOMIZE_FRACTION)

        place = PlacePrototype.get_by_coordinates(x, y)

        dominant_race = None
        place_modifiers = None

        chronicle_records = []

        if place is not None:

            dominant_race = RACE_MULTIPLE_VERBOSE[place.race.value]

            place_modifiers = place.modifiers

            chronicle_records = RecordPrototype.get_last_actor_records(place, map_settings.CHRONICLE_RECORDS_NUMBER)

        terrain_points = []

        if self.user.is_staff:
            for terrain_id, text in TERRAIN._ID_TO_TEXT.items():
                biom = Biom(id_=terrain_id)
                terrain_points.append((text, biom.check(cell), biom.get_points(cell)))
            terrain_points = sorted(terrain_points, key=lambda x: -x[1])


        return self.template('map/cell_info.html',
                             {'place': place,
                              'place_modifiers': place_modifiers,
                              'cell': cell,
                              'cell_power': cell_power,
                              'descr_wind': descriptors.wind(randomized_cell),
                              'descr_temperature': descriptors.temperature(randomized_cell),
                              'descr_wetness': descriptors.wetness(randomized_cell),
                              'terrain': terrain,
                              'nearest_place_name': nearest_place_name,
                              'dominant_race': dominant_race,
                              'x': x,
                              'y': y,
                              'terrain_points': terrain_points,
                              'chronicle_records': chronicle_records,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account else None} )
