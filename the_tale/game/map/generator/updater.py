# coding: utf-8
import os
import math

import deworld

from dext.utils import s11n

from game.prototypes import TimePrototype

from game.map.conf import map_settings
from game.map.storage import map_info_storage
from game.map.prototypes import MapInfoPrototype
from game.map.generator import biomes
from game.map.generator.power_points import get_places_power_points
from game.map.places.storage import places_storage
from game.map.places.models import TERRAIN
from game.map.roads.storage import roads_storage


class PATH_DIRECTION:
    LEFT = 'l'
    RIGHT = 'r'
    UP = 'u'
    DOWN = 'd'


def _place_info(place):
    return {'id': place.id,
            'x': place.x,
            'y': place.y,
            'name': place.name,
            'size': place.size}


def _road_info(road):
    return {'id': road.id,
            'point_1_id': road.point_1.id,
            'point_2_id': road.point_2.id,
            'path': roll_road(road.point_1.x, road.point_1.y, road.point_2.x, road.point_2.y),
            'length': road.length,
            'exists': road.exists}


def roll_road(start_x, start_y, finish_x, finish_y):

    path = []

    x = start_x
    y = start_y

    if math.fabs(finish_x - start_x) >  math.fabs(finish_y - start_y):
        dx = math.copysign(1.0, finish_x - start_x)
        dy = dx * float(finish_y - start_y) / (finish_x - start_x)
    else:
        dy = math.copysign(1.0, finish_y - start_y)
        dx = dy * float(finish_x - start_x) / (finish_y - start_y)

    real_x = float(x)
    real_y = float(y)

    while x != finish_x or y != finish_y:

        real_x += dx
        real_y += dy

        if int(round(real_x)) == x + 1: path.append(PATH_DIRECTION.RIGHT)
        elif int(round(real_x)) == x - 1: path.append(PATH_DIRECTION.LEFT)

        if int(round(real_y)) == y + 1: path.append(PATH_DIRECTION.DOWN)
        elif int(round(real_y)) == y - 1: path.append(PATH_DIRECTION.UP)

        x = int(round(real_x))
        y = int(round(real_y))

    return ''.join(path)


def update_map(index):

    world = map_info_storage.item.world

    world.clear_power_points()
    world.clear_biomes()

    for point in get_places_power_points():
        world.add_power_point(point)

    world.add_biom(biomes.Mountains(id_=TERRAIN.MOUNTAINS))
    world.add_biom(biomes.Desert(id_=TERRAIN.DESERT))
    world.add_biom(biomes.Swamp(id_=TERRAIN.SWAMP))
    world.add_biom(biomes.Forest(id_=TERRAIN.FOREST))
    world.add_biom(biomes.Grass(id_=TERRAIN.GRASS))
    world.add_biom(biomes.Default(id_=TERRAIN.GRASS))

    world.do_step()

    biomes_map = world.get_biomes_map()

    time = TimePrototype.get_current_time()

    terrain = []
    for y in xrange(0, world.h):
        row = []
        terrain.append(row)
        for x in xrange(0, world.w):
            row.append(biomes_map[y][x].id)

    map_info_storage.set_item(MapInfoPrototype.create(turn_number=time.turn_number,
                                                      width=world.w,
                                                      height=world.h,
                                                      terrain=terrain,
                                                      world=world))

    data = {'width': world.w,
            'height': world.h,
            'terrain': [ ''.join(row) for row in terrain ],
            'places': dict( (place.id, _place_info(place) ) for place in places_storage.all() ),
            'roads': dict( (road.id, _road_info(road) ) for road in roads_storage.all() ) }


    output_dir_name = os.path.dirname(map_settings.GEN_REGION_OUTPUT)
    if not os.path.exists(output_dir_name):
        os.makedirs(output_dir_name, 0755)

    with open(map_settings.GEN_REGION_OUTPUT, 'w') as region_json_file:
        region_json_file.write(s11n.to_json(data).encode('utf-8'))

    deworld.draw_world(index, world, catalog=map_settings.GEN_WORLD_PROGRESSION)
