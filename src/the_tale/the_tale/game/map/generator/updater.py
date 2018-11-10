
import smart_imports

smart_imports.all()


def update_map(index):

    generator = prototypes.WorldInfoPrototype.get_by_id(storage.map_info.item.world_id).generator

    generator.clear_power_points()
    generator.clear_biomes()

    if generator.w != conf.settings.WIDTH or generator.h != conf.settings.HEIGHT:
        dx, dy = generator.resize(conf.settings.WIDTH, conf.settings.HEIGHT)
        places_storage.places.shift_all(dx, dy)
        places_storage.buildings.shift_all(dx, dy)

    for point in power_points.get_power_points():
        generator.add_power_point(point)

    for terrain in relations.TERRAIN.records:
        generator.add_biom(biomes.Biom(id_=terrain))

    generator.do_step()

    biomes_map = generator.get_biomes_map()

    draw_info = drawer.get_draw_info(biomes_map)

    terrain = []
    for y in range(0, generator.h):
        row = []
        terrain.append(row)
        for x in range(0, generator.w):
            row.append(biomes_map[y][x].id)

    storage.map_info.set_item(prototypes.MapInfoPrototype.create(turn_number=game_turn.number(),
                                                                 width=generator.w,
                                                                 height=generator.h,
                                                                 terrain=terrain,
                                                                 world=prototypes.WorldInfoPrototype.create_from_generator(generator)))

    prototypes.MapInfoPrototype.remove_old_infos()

    raw_draw_info = []
    for row in draw_info:
        raw_draw_info.append([])
        for cell in row:
            raw_draw_info[-1].append(cell.get_sprites())

    data = {'width': generator.w,
            'height': generator.h,
            'map_version': storage.map_info.version,
            'format_version': '0.1',
            'draw_info': raw_draw_info,
            'places': dict((place.id, place.map_info()) for place in places_storage.places.all()),
            # 'buildings': dict( (building.id, building.map_info() ) for building in buildings_storage.all() ),
            'roads': dict((road.id, road.map_info()) for road in roads_storage.roads.all())}

    try:
        models.MapRegion.objects.create(turn_number=game_turn.number(), data=data)
    except django_db_utils.IntegrityError:
        models.MapRegion.objects.filter(turn_number=game_turn.number()).update(data=data)
