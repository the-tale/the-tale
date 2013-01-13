# coding: utf-8

from dext.utils import s11n
import deworld

from game.balance.enums import RACE

from game.persons.models import Person, PERSON_STATE
from game.persons.prototypes import PersonPrototype

from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype
from game.map.places.storage import places_storage

from game.map.models import MapInfo
from game.map.conf import map_settings


class MapInfoPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def turn_number(self): return self.model.turn_number

    @property
    def terrain(self):
        if not hasattr(self, '_terrain'):
            self._terrain = s11n.from_json(self.model.terrain)
        return self._terrain

    @property
    def statistics(self):
        if not hasattr(self, '_statistics'):
            self._statistics = s11n.from_json(self.model.statistics)
            self._statistics['race_percents'] = dict( (int(key), value) for key, value in self._statistics['race_percents'].items())
            self._statistics['race_cities'] = dict( (int(key), value) for key, value in self._statistics['race_cities'].items())
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
            if not self.model.world:
                self._world = self._create_world(w=map_settings.WIDTH, h=map_settings.HEIGHT)
            else:
                world_data = s11n.from_json(self.model.world)
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
    def create(cls, turn_number, width, height, terrain, world):

        # terrain percents
        terrain_squares = {}

        for row in terrain:
            for cell in row:
                terrain_squares[cell] = terrain_squares.get(cell, 0) + 1

        total_cells = sum(terrain_squares.values())

        terrain_percents = dict( (cell, float(square) / total_cells) for cell, square in terrain_squares.items())

        # race percents
        race_powers = dict( (race_id, 0) for race_id in RACE._ALL)
        for person_model in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            person = PersonPrototype(person_model)
            race_powers[person.race] += person.power

        total_power = sum(race_powers.values()) + 1 # +1 - to prevent division by 0

        race_percents = dict( (race_id, float(power) / total_power) for race_id, power in race_powers.items())

        #race to cities percents
        race_cities = dict( (race_id, 0) for race_id in RACE._ALL)
        for place_model in Place.objects.all():
            place = PlacePrototype(place_model)
            race_cities[place.get_dominant_race()] += 1


        statistics = {'terrain_percents': terrain_percents,
                      'race_percents': race_percents,
                      'race_cities': race_cities}

        model = MapInfo.objects.create(turn_number=turn_number,
                                       width=width,
                                       height=height,
                                       terrain=s11n.to_json(terrain),
                                       world=s11n.to_json(world.serialize()),
                                       statistics=s11n.to_json(statistics))
        return cls(model)
