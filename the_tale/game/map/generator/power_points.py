# coding: utf-8
import math

from deworld import power_points, layers, normalizers

from game.balance.enums import RACE

from game.map.places.storage import places_storage
from game.map.exceptions import MapException
from game.map.conf import map_settings

def get_height_power_function(borders):

    def power_function(world, x, y):
        height = world.layer_height.data[y][x]

        if height < borders[0]: return (0.0, math.fabs(borders[0] - height))
        if height > borders[1]: return (math.fabs(borders[1] - height), 0.0)

        optimal = (borders[0] + borders[1]) / 2

        if height < optimal: return (0.0, math.fabs(borders[0] - height) / 2)
        if height > optimal: return (math.fabs(borders[1] - height) / 2, 0.0)

        return (0.0, 0.0)

    return power_function


def _point_circle_height(place, borders, normalizer):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.HEIGHT,
                                        name='place_height_point_%d' % place.id,
                                        x=place.x,
                                        y=place.y,
                                        radius=place.terrain_change_power,
                                        power=get_height_power_function(borders),
                                        default_power=(0.0, 0.0),
                                        normalizer=normalizer)


def _point_arrow_height(place, borders, length_normalizer, width_normalizer):

    distances = []

    for other_place in places_storage.all():
        if place.id != other_place.id:
            distances.append((math.hypot(place.x - other_place.x, place.y - other_place.y), other_place))

    distances = sorted(distances, key=lambda x: x[0])

    arrows = []

    if len(distances) > 0:
        distance, other_place = distances[0]
        arrow = power_points.ArrowAreaPoint.Arrow(angle=math.atan2(other_place.y - place.y, other_place.x - place.x),
                                                  length=place.terrain_change_power,
                                                  width=(place.terrain_change_power / 3) + 1)
        arrows.extend([arrow, arrow.rounded_arrow])

    if len(distances) > 1:
        distance, other_place = distances[1]
        arrow = power_points.ArrowAreaPoint.Arrow(angle=math.atan2(other_place.y - place.y, other_place.x - place.x),
                                                  length=place.terrain_change_power,
                                                  width=(place.terrain_change_power / 3) + 1)
        arrows.extend([arrow, arrow.rounded_arrow])

    return power_points.ArrowAreaPoint(layer_type=layers.LAYER_TYPE.HEIGHT,
                                       name='place_height_point_%d' % place.id,
                                       x=place.x,
                                       y=place.y,
                                       power=get_height_power_function(borders),
                                       default_power=(0.0, 0.0),
                                       length_normalizer=length_normalizer,
                                       width_normalizer=width_normalizer,
                                       arrows=arrows)

def _point_circle_vegetation(place, power, normalizer):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.VEGETATION,
                                        name='place_vegetation_point_%d' % place.id,
                                        x=place.x,
                                        y=place.y,
                                        radius=place.terrain_change_power,
                                        power=power,
                                        default_power=(0.0, 0.0),
                                        normalizer=normalizer)

def _point_circle_soil(place, power, normalizer):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.SOIL,
                                        name='place_soil_point_%d' % place.id,
                                        x=place.x,
                                        y=place.y,
                                        radius=place.terrain_change_power,
                                        power=power,
                                        default_power=0.0,
                                        normalizer=normalizer)

def _point_circle_temperature(place, power, normalizer):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.TEMPERATURE,
                                        name='place_temperature_point_%d' % place.id,
                                        x=place.x,
                                        y=place.y,
                                        radius=place.terrain_change_power,
                                        power=power,
                                        normalizer=normalizer)

def _point_circle_wetness(place, power, normalizer):
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.WETNESS,
                                        name='place_wetness_point_%d' % place.id,
                                        x=place.x,
                                        y=place.y,
                                        radius=place.terrain_change_power,
                                        power=power,
                                        normalizer=normalizer)

def _default_temperature_points():
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.TEMPERATURE,
                                        name='default_temperature',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=0.5,
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)


def _default_wetness_points():
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.WETNESS,
                                        name='default_wetness',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=0.6,
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)

def _default_vegetation_points():
    return power_points.CircleAreaPoint(layer_type=layers.LAYER_TYPE.VEGETATION,
                                        name='default_vegetation',
                                        x=map_settings.WIDTH/2,
                                        y=map_settings.HEIGHT/2,
                                        power=(0.2, 0.2),
                                        default_power=(0.0, 0.0),
                                        radius=int(math.hypot(map_settings.WIDTH, map_settings.HEIGHT)/2)+1,
                                        normalizer=normalizers.equal)



def get_places_power_points():

    points = []

    points = [_default_temperature_points(),
              _default_wetness_points(),
              _default_vegetation_points()]

    for place in places_storage.all():
        race = place.get_dominant_race()

        if race == RACE.HUMAN:
            points.append(_point_circle_height(place=place, borders=(-0.2, 0.2), normalizer=normalizers.linear_2))
            points.append(_point_circle_vegetation(place=place, power=(0.6, -0.3), normalizer=normalizers.linear_2))
            points.append(_point_circle_soil(place=place, power=0.2, normalizer=normalizers.linear))
            points.append(_point_circle_wetness(place=place, power=0.1, normalizer=normalizers.linear))
        elif race == RACE.ELF:
            points.append(_point_circle_height(place=place, borders=(0.0, 0.6), normalizer=normalizers.linear_2))
            points.append(_point_circle_vegetation(place=place, power=(-0.2, 1.0), normalizer=normalizers.linear_2))
            points.append(_point_circle_soil(place=place, power=0.1, normalizer=normalizers.linear))
            points.append(_point_circle_temperature(place=place, power=0.1, normalizer=normalizers.linear))
            points.append(_point_circle_wetness(place=place, power=0.1, normalizer=normalizers.linear))
        elif race == RACE.ORC:
            points.append(_point_circle_height(place=place, borders=(-0.2, 0.3), normalizer=normalizers.linear_2))
            points.append(_point_circle_vegetation(place=place, power=(-0.3, -0.5), normalizer=normalizers.linear_2))
            points.append(_point_circle_temperature(place=place, power=0.3, normalizer=normalizers.linear))
            points.append(_point_circle_wetness(place=place, power=-0.5, normalizer=normalizers.linear))
        elif race == RACE.GOBLIN:
            points.append(_point_circle_height(place=place, borders=(-0.7, -0.3), normalizer=normalizers.linear_2))
            points.append(_point_circle_vegetation(place=place, power=(0.2, 0.0), normalizer=normalizers.linear_2))
            points.append(_point_circle_soil(place=place, power=-0.2, normalizer=normalizers.linear))
            points.append(_point_circle_temperature(place=place, power=0.4, normalizer=normalizers.linear))
            points.append(_point_circle_wetness(place=place, power=0.5, normalizer=normalizers.linear))
        elif race == RACE.DWARF:
            points.append(_point_arrow_height(place=place, borders=(1.0, 1.0), length_normalizer=normalizers.linear_2, width_normalizer=normalizers.linear_2))
            points.append(_point_circle_temperature(place=place, power=0.1, normalizer=normalizers.linear))
            points.append(_point_circle_vegetation(place=place, power=(0.0, -0.1), normalizer=normalizers.linear_2))
            points.append(_point_circle_wetness(place=place, power=-0.1, normalizer=normalizers.linear))
        else:
            raise MapException('unknown place dominant race: %r' % race)

    return points
