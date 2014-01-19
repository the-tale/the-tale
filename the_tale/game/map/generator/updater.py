# coding: utf-8
import os

import deworld

from dext.utils import s11n

from django.conf import settings as project_settings

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.conf import map_settings
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from the_tale.game.map.generator.biomes import Biom
from the_tale.game.map.generator.power_points import get_power_points
from the_tale.game.map.generator.drawer import get_draw_info
from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.map.roads.storage import roads_storage
from the_tale.game.map.relations import TERRAIN



def update_map(index):

    generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

    generator.clear_power_points()
    generator.clear_biomes()

    if generator.w != map_settings.WIDTH or generator.h != map_settings.HEIGHT:
        dx, dy = generator.resize(map_settings.WIDTH, map_settings.HEIGHT)
        places_storage.shift_all(dx, dy)
        buildings_storage.shift_all(dx, dy)

    for point in get_power_points():
        generator.add_power_point(point)

    for terrain in TERRAIN.records:
        generator.add_biom(Biom(id_=terrain))

    generator.do_step()

    biomes_map = generator.get_biomes_map()

    time = TimePrototype.get_current_time()

    draw_info = get_draw_info(biomes_map)

    terrain = []
    for y in xrange(0, generator.h):
        row = []
        terrain.append(row)
        for x in xrange(0, generator.w):
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
            'places': dict( (place.id, place.map_info() ) for place in places_storage.all() ),
            # 'buildings': dict( (building.id, building.map_info() ) for building in buildings_storage.all() ),
            'roads': dict( (road.id, road.map_info() ) for road in roads_storage.all()) }

    region_js_file = map_settings.GEN_REGION_OUTPUT % map_info_storage.version

    output_dir_name = os.path.dirname(region_js_file)
    if not os.path.exists(output_dir_name):
        os.makedirs(output_dir_name, 0755)

    with open(region_js_file, 'w') as region_json_file:
        region_json_file.write(s11n.to_json(data).encode('utf-8'))

    if project_settings.DEBUG:
        deworld.draw_world(index, generator, catalog=map_settings.GEN_WORLD_PROGRESSION)
