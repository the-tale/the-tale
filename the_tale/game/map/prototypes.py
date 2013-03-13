# coding: utf-8

from collections import defaultdict

from dext.utils import s11n

import deworld

from deworld.layers import VEGETATION_TYPE

from common.utils.prototypes import BasePrototype

from game.balance.enums import RACE

from game.persons.models import PERSON_STATE
from game.persons.storage import persons_storage

from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype
from game.map.places.storage import places_storage

from game.map.models import MapInfo
from game.map.conf import map_settings
from game.map.utils import get_race_percents

from game.map.relations import MAP_STATISTICS


class MapInfoPrototype(BasePrototype):
    _model_class = MapInfo
    _readonly = ('id', 'turn_number')

    @property
    def terrain(self):
        if not hasattr(self, '_terrain'):
            self._terrain = s11n.from_json(self._model.terrain)
        return self._terrain

    @property
    def statistics(self):
        if not hasattr(self, '_statistics'):
            self._statistics = s11n.from_json(self._model.statistics)
            self._statistics['race_percents'] = dict( (int(key), value) for key, value in self._statistics['race_percents'].items())
            self._statistics['race_cities'] = dict( (int(key), value) for key, value in self._statistics['race_cities'].items())
            self._statistics['terrain_percents'] = dict( (int(key), value) for key, value in self._statistics['terrain_percents'].items())
        return self._statistics

    @property
    def terrain_percents(self):
        return self.statistics['terrain_percents']

    @property
    def race_percents(self): return self.statistics['race_percents']

    @property
    def race_cities(self): return self.statistics['race_cities']

    @property
    def world(self):
        if not hasattr(self, '_world'):
            if not self._model.world:
                self._world = self._create_world(w=map_settings.WIDTH, h=map_settings.HEIGHT)
            else:
                world_data = s11n.from_json(self._model.world)
                self._world = deworld.World.deserialize(config=deworld.BaseConfig, data=world_data)
        return self._world

    @classmethod
    def _create_world(self, w, h):
        return deworld.World(w=w, h=h, config=deworld.BaseConfig)

    def get_dominant_place(self, x, y):
        for place in places_storage.all():
            if (x, y) in place.nearest_cells:
                return place
        return None

    ######################
    # object operations
    ######################

    @classmethod
    def remove_old_infos(cls):
        new_ids =  MapInfo.objects.order_by('-created_at', '-turn_number')[:2].values_list('id', flat=True)
        MapInfo.objects.exclude(id__in=new_ids).delete()

    @classmethod
    def create(cls, turn_number, width, height, terrain, world=None):
        '''
        if world is None, it will be created in world property
        '''

        # terrain percents
        terrain_percents = {}

        if world:

            terrain_squares = defaultdict(int)

            for y in xrange(0, height):
                for x in xrange(0, width):
                    cell = world.cell_info(x, y)

                    if cell.height < -0.2:
                        terrain_squares[MAP_STATISTICS.LOWLANDS] += 1
                    elif cell.height < 0.3:
                        terrain_squares[MAP_STATISTICS.PLAINS] += 1
                    else:
                        terrain_squares[MAP_STATISTICS.UPLANDS] += 1

                    if cell.vegetation == VEGETATION_TYPE.DESERT:
                        terrain_squares[MAP_STATISTICS.DESERTS] += 1
                    elif cell.vegetation == VEGETATION_TYPE.GRASS:
                        terrain_squares[MAP_STATISTICS.GRASS] += 1
                    else:
                        terrain_squares[MAP_STATISTICS.FORESTS] += 1

            total_cells = width * height

            terrain_percents = dict( (id_, float(square) / total_cells) for id_, square in terrain_squares.items())

        race_percents = get_race_percents(persons_storage.filter(state=PERSON_STATE.IN_GAME))

        #race to cities percents
        race_cities = dict( (race_id, 0) for race_id in RACE._ALL)
        for place_model in Place.objects.all():
            place = PlacePrototype(place_model)
            race_cities[place.race.value] += 1


        statistics = {'terrain_percents': terrain_percents,
                      'race_percents': race_percents,
                      'race_cities': race_cities}

        model = MapInfo.objects.create(turn_number=turn_number,
                                       width=width,
                                       height=height,
                                       terrain=s11n.to_json(terrain),
                                       world=s11n.to_json(world.serialize()) if world else '',
                                       statistics=s11n.to_json(statistics))
        return cls(model)
