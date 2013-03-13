# coding: utf-8
import os

import deworld

from dext.utils import s11n

from django.conf import settings as project_settings

from game.prototypes import TimePrototype

from game.map.conf import map_settings
from game.map.storage import map_info_storage
from game.map.prototypes import MapInfoPrototype
from game.map.generator.biomes import Biom
from game.map.generator.power_points import get_places_power_points
from game.map.places.storage import places_storage, buildings_storage
from game.map.relations import TERRAIN
from game.map.roads.storage import roads_storage


def update_map(index):

    world = map_info_storage.item.world

    world.clear_power_points()
    world.clear_biomes()

    if world.w != map_settings.WIDTH or world.h != map_settings.HEIGHT:
        world.resize(map_settings.WIDTH, map_settings.HEIGHT)

    for point in get_places_power_points():
        world.add_power_point(point)

    for terrain in TERRAIN._ALL:
        world.add_biom(Biom(id_=terrain))

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

    MapInfoPrototype.remove_old_infos()

    data = {'width': world.w,
            'height': world.h,
            'map_version': map_info_storage.version,
            'terrain': [ row for row in terrain ],
            'places': dict( (place.id, place.map_info() ) for place in places_storage.all() ),
            'buildings': dict( (building.id, building.map_info() ) for building in buildings_storage.all() ),
            'roads': dict( (road.id, road.map_info() ) for road in roads_storage.all() ) }


    output_dir_name = os.path.dirname(map_settings.GEN_REGION_OUTPUT)
    if not os.path.exists(output_dir_name):
        os.makedirs(output_dir_name, 0755)

    with open(map_settings.GEN_REGION_OUTPUT, 'w') as region_json_file:
        region_json_file.write(s11n.to_json(data).encode('utf-8'))

    if project_settings.DEBUG:
        deworld.draw_world(index, world, catalog=map_settings.GEN_WORLD_PROGRESSION)
