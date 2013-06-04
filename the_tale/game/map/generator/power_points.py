# coding: utf-8
import math

from deworld import power_points, layers, normalizers

from game.balance.enums import RACE

from game.prototypes import TimePrototype, MONTHS

from game.persons.prototypes import PersonPrototype

from game.map.places.prototypes import PlacePrototype, BuildingPrototype
from game.map.places.storage import places_storage, buildings_storage
from game.map.exceptions import MapException
from game.map.conf import map_settings

def get_height_power_function(borders, power_percent):

    def power_function(world, x, y):
        height = world.layer_height.data[y][x]

        if height < borders[0]: return (0.0, math.fabs(borders[0] - height) * power_percent)
        if height > borders[1]: return (math.fabs(borders[1] - height) * power_percent, 0.0)

        optimal = (borders[0] + borders[1]) / 2

        if height < optimal: return (0.0, math.fabs(borders[0] - height) / 2 * power_percent)
        if height > optimal: return (math.fabs(borders[1] - height) / 2 * power_percent, 0.0)

        return (0.0, 0.0)

    return power_function


def _point_circle_height(obj, borders, normalizer, power_percent):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.HEIGHT,
                                        name='height_circle_' + obj.uid,
                                        x=obj.x,
                                        y=obj.y,
                                        radius=obj.r,
                                        power=get_height_power_function(borders, power_percent),
                                        default_power=(0.0, 0.0),
                                        normalizer=normalizer)

class MapObject(object):

    def __init__(self, game_object):
        if isinstance(game_object, PlacePrototype):
            self.uid = 'place_%d' % game_object.id
            self.x = game_object.x
            self.y = game_object.y
            self.r = game_object.terrain_change_power
        elif isinstance(game_object, PersonPrototype):
            self.uid = 'person_%d' % game_object.id
            self.x = game_object.place.x
            self.y = game_object.place.y
            self.r = game_object.place.terrain_change_power
        elif isinstance(game_object, BuildingPrototype):
            self.uid = 'building_%d' % game_object.id
            self.x = game_object.x
            self.y = game_object.y
            self.r = game_object.terrain_change_power
        else:
            raise MapException('try to get uid for unknown power point source %r' % game_object)

        self.id = game_object.id


def _point_arrow_height(obj, borders, length_normalizer, width_normalizer, power_percent):

    distances = []

    for other_place in places_storage.all():
        if obj.id != other_place.id:
            distances.append((math.hypot(obj.x - other_place.x, obj.y - other_place.y), other_place))

    distances = sorted(distances, key=lambda x: x[0])

    arrows = []

    if len(distances) > 0:
        distance, other_place = distances[0] # pylint: disable=W0612
        arrow = power_points.ArrowAreaPoint.Arrow(angle=math.atan2(other_place.y - obj.y, other_place.x - obj.x),
                                                  length=obj.r,
                                                  width=(obj.r / 3) + 1)
        arrows.extend([arrow, arrow.rounded_arrow])

    if len(distances) > 1:
        distance, other_place = distances[1]
        arrow = power_points.ArrowAreaPoint.Arrow(angle=math.atan2(other_place.y - obj.y, other_place.x - obj.x),
                                                  length=obj.r,
                                                  width=(obj.r / 3) + 1)
        arrows.extend([arrow, arrow.rounded_arrow])

    return power_points.ArrowAreaPoint(layer_type=layers.LAYER_TYPE.HEIGHT,
                                       name='height_arrow_' + obj.uid,
                                       x=obj.x,
                                       y=obj.y,
                                       power=get_height_power_function(borders, power_percent),
                                       default_power=(0.0, 0.0),
                                       length_normalizer=length_normalizer,
                                       width_normalizer=width_normalizer,
                                       arrows=arrows)

def _point_circle_vegetation(obj, power, normalizer, power_percent):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.VEGETATION,
                                        name='vegetation_' + obj.uid,
                                        x=obj.x,
                                        y=obj.y,
                                        radius=obj.r,
                                        power=(power[0] * power_percent, power[1] * power_percent),
                                        default_power=(0.0, 0.0),
                                        normalizer=normalizer)

def _point_circle_soil(obj, power, normalizer, power_percent):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.SOIL,
                                        name='soil_' + obj.uid,
                                        x=obj.x,
                                        y=obj.y,
                                        radius=obj.r,
                                        power=power * power_percent,
                                        default_power=0.0,
                                        normalizer=normalizer)

def _point_circle_temperature(obj, power, normalizer, power_percent):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.TEMPERATURE,
                                        name='temperature_' + obj.uid,
                                        x=obj.x,
                                        y=obj.y,
                                        radius=obj.r,
                                        power=power * power_percent,
                                        normalizer=normalizer)

def _point_circle_wetness(obj, power, normalizer, power_percent):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.WETNESS,
                                        name='wetness_' + obj.uid,
                                        x=obj.x,
                                        y=obj.y,
                                        radius=obj.r,
                                        power=power * power_percent,
                                        normalizer=normalizer)

def _default_temperature_points(delta=0.0):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.TEMPERATURE,
                                        name='default_temperature',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=0.5 + delta,
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)


def _default_wetness_points(delta=0.0):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.WETNESS,
                                        name='default_wetness',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=0.6 + delta,
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)

def _default_soil_points(delta=0.0):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.SOIL,
                                        name='default_soil',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=0.3 + delta,
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)

def _default_vegetation_points():
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.VEGETATION,
                                        name='default_vegetation',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=(0.25, 0.25),
                                        default_power=(0.0, 0.0),
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)


def get_building_power_points(building): # pylint: disable=R0912,R0915

    points = []

    if building.type._is_SMITHY:
        points.append(_point_arrow_height(MapObject(building), borders=(0.3, 1.0), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, -0.4), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.1, normalizer=normalizers.linear, power_percent=1.0))
        points.append(_point_circle_wetness(MapObject(building), power=-0.2, normalizer=normalizers.linear, power_percent=1.0))
        points.append(_point_circle_temperature(MapObject(building), power=0.15, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_FISHING_LODGE:
        # points.append(_point_circle_height(MapObject(building), borders=(-0.8, -0.4), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_wetness(MapObject(building), power=0.2, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_TAILOR_SHOP:
        points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_SAWMILL:
        points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, 0.3), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_HUNTER_HOUSE:
        points.append(_point_circle_height(MapObject(building), borders=(-0.7, 0.7), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_WATCHTOWER:
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, -0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_TRADING_POST:
        # points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.1, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_INN:
        points.append(_point_circle_soil(MapObject(building), power=-0.01, normalizer=normalizers.linear, power_percent=1.0))
        # points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_DEN_OF_THIEVE:
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, 0.3), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_FARM:
        points.append(_point_circle_height(MapObject(building), borders=(0.0, 0.0), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.3, -0.3), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_MINE:
        points.append(_point_arrow_height(MapObject(building), borders=(1.0, 1.0), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.1, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_TEMPLE:
        points.append(_point_circle_height(MapObject(building), borders=(0.3, 1.0), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_HOSPITAL:
        points.append(_point_circle_height(MapObject(building), borders=(0.0, 0.4), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, 0.1), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_LABORATORY:
        points.append(_point_arrow_height(MapObject(building), borders=(0.4, 0.8), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.3, normalizer=normalizers.linear, power_percent=1.0))
        points.append(_point_circle_temperature(MapObject(building), power=0.1, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_SCAFFOLD:
        points.append(_point_circle_height(MapObject(building), borders=(0.2, 0.4), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_MAGE_TOWER:
        points.append(_point_arrow_height(MapObject(building), borders=(0.4, 1.0), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.2, normalizer=normalizers.linear, power_percent=1.0))
        points.append(_point_circle_temperature(MapObject(building), power=0.1, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_GUILDHALL:
        points.append(_point_circle_soil(MapObject(building), power=-0.01, normalizer=normalizers.linear, power_percent=1.0))
        # points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_BUREAU:
        points.append(_point_circle_soil(MapObject(building), power=-0.01, normalizer=normalizers.linear, power_percent=1.0))
        # points.append(_point_circle_height(MapObject(building), borders=(-0.5, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_MANOR:
        points.append(_point_circle_soil(MapObject(building), power=-0.01, normalizer=normalizers.linear, power_percent=1.0))
        # points.append(_point_circle_height(MapObject(building), borders=(0.2, 0.5), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_SCENE:
        # points.append(_point_circle_height(MapObject(building), borders=(0.2, 0.4), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, -0.1), normalizer=normalizers.linear_2, power_percent=1.0))
    elif building.type._is_MEWS:
        points.append(_point_circle_height(MapObject(building), borders=(-0.2, 0.2), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, -0.6), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.15, normalizer=normalizers.linear, power_percent=1.0))
    elif building.type._is_RANCH:
        points.append(_point_circle_height(MapObject(building), borders=(-0.2, 0.2), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_vegetation(MapObject(building), power=(0.0, -0.6), normalizer=normalizers.linear_2, power_percent=1.0))
        points.append(_point_circle_soil(MapObject(building), power=-0.2, normalizer=normalizers.linear, power_percent=1.0))
    else:
        raise MapException('unknown building type: %r' % building.type)

    return points

def get_person_power_points(person):

    place_power = person.place.total_persons_power

    if place_power < 0.1:
        return []

    power_percent = person.power / place_power * 0.5

    return get_object_race_points(MapObject(person), person.race, power_percent)


def get_place_power_points(place):
    return get_object_race_points(MapObject(place), place.race, 1.0)


def get_object_race_points(obj, race, power_percent):
    points = []

    if race == RACE.HUMAN:
        points.append(_point_circle_height(obj, borders=(-0.2, 0.2), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_vegetation(obj, power=(0.6, -0.3), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_soil(obj, power=0.2, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_wetness(obj, power=-0.05, normalizer=normalizers.linear, power_percent=power_percent))
    elif race == RACE.ELF:
        points.append(_point_circle_height(obj, borders=(0.0, 0.5), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_vegetation(obj, power=(-0.2, 1.0), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_soil(obj, power=0.1, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_temperature(obj, power=0.1, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_wetness(obj, power=0.1, normalizer=normalizers.linear, power_percent=power_percent))
    elif race == RACE.ORC:
        points.append(_point_circle_height(obj, borders=(-0.2, 0.3), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_vegetation(obj, power=(-0.3, -0.5), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_temperature(obj, power=0.3, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_wetness(obj, power=-0.5, normalizer=normalizers.linear, power_percent=power_percent))
    elif race == RACE.GOBLIN:
        points.append(_point_circle_height(obj, borders=(-0.7, -0.3), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_vegetation(obj, power=(0.2, 0.0), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_soil(obj, power=-0.2, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_temperature(obj, power=0.2, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_wetness(obj, power=0.4, normalizer=normalizers.linear, power_percent=power_percent))
    elif race == RACE.DWARF:
        points.append(_point_arrow_height(obj, borders=(1.0, 1.0), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_temperature(obj, power=0.1, normalizer=normalizers.linear, power_percent=power_percent))
        points.append(_point_circle_vegetation(obj, power=(0.0, -0.1), normalizer=normalizers.linear_2, power_percent=power_percent))
        points.append(_point_circle_wetness(obj, power=-0.1, normalizer=normalizers.linear, power_percent=power_percent))
    else:
        raise MapException('unknown person race: %r' % race)

    return points


def get_power_points():

    month = TimePrototype.get_current_time().game_time.month_record

    points = []

    points = [_default_temperature_points(delta={MONTHS.COLD: -0.1, MONTHS.HOT: 0.1}.get(month, 0)),
              _default_wetness_points(delta={MONTHS.DRY: -0.1, MONTHS.CRUDE: 0.1}.get(month, 0)),
              _default_vegetation_points(),
              _default_soil_points()]

    for place in places_storage.all():
        points.extend(get_place_power_points(place))
        for person in place.persons:
            points.extend(get_person_power_points(person))

    for building in buildings_storage.all():
        points.extend(get_building_power_points(building))

    return points
