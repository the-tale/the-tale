# coding: utf-8
import os

import deworld

from dext.common.utils import s11n

from django.conf import settings as project_settings

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.conf import map_settings
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from the_tale.game.map.generator.biomes import Biom
from the_tale.game.map.generator.power_points import get_power_points
from the_tale.game.map.generator.drawer import get_draw_info
from the_tale.game.places import storage as places_storage
from the_tale.game.roads.storage import roads_storage
from the_tale.game.map.relations import TERRAIN
from the_tale.game.map import models



def update_map(index):

    generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

    generator.clear_power_points()
    generator.clear_biomes()

    if generator.w != map_settings.WIDTH or generator.h != map_settings.HEIGHT:
        dx, dy = generator.resize(map_settings.WIDTH, map_settings.HEIGHT)
        places_storage.places.shift_all(dx, dy)
        places_storage.buildings.shift_all(dx, dy)

    for point in get_power_points():
        generator.add_power_point(point)

    for terrain in TERRAIN.records:
        generator.add_biom(Biom(id_=terrain))

    generator.do_step()

    biomes_map = generator.get_biomes_map()

    time = TimePrototype.get_current_time()

    draw_info = get_draw_info(biomes_map)

    terrain = []
    for y in range(0, generator.h):
        row = []
        terrain.append(row)
        for x in range(0, generator.w):
            row.append(biomes_map[y][x].id)

    map_info_storage.set_item(MapInfoPrototype.create(turn_number=time.turn_number,
                                                      width=generator.w,
                                                      height=generator.h,
                                                      terrain=terrain,
                                                      world=WorldInfoPrototype.create_from_generator(generator)))

    MapInfoPrototype.remove_old_infos()

    raw_draw_info = []
    for row in draw_info:
        raw_draw_info.append([])
        for cell in row:
            raw_draw_info[-1].append(cell.get_sprites())

    data = {'width': generator.w,
            'height': generator.h,
            'map_version': map_info_storage.version,
            'format_version': '0.1',
            'draw_info': raw_draw_info,
            'places': dict( (place.id, place.map_info() ) for place in places_storage.places.all() ),
            # 'buildings': dict( (building.id, building.map_info() ) for building in buildings_storage.all() ),
            'roads': dict( (road.id, road.map_info() ) for road in roads_storage.all()) }

    models.MapRegion.objects.create(turn_number=time.turn_number, data=data)
