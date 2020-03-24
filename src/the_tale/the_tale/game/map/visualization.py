
import smart_imports

smart_imports.all()


OUTPUT_RECTANGLE = (0 * conf.settings.CELL_SIZE,
                    0 * conf.settings.CELL_SIZE,
                    70 * conf.settings.CELL_SIZE,
                    70 * conf.settings.CELL_SIZE)


REAL_SIZE = ((OUTPUT_RECTANGLE[2] - OUTPUT_RECTANGLE[0]),
             (OUTPUT_RECTANGLE[3] - OUTPUT_RECTANGLE[1]))


def draw_sprite(image, texture, sprite_info, x, y, rotate=0, base=False):

    sprite_borders = (sprite_info.x, sprite_info.y,
                      sprite_info.x + conf.settings.CELL_SIZE, sprite_info.y + conf.settings.CELL_SIZE)

    sprite = texture.crop(sprite_borders)

    if rotate:
        sprite = sprite.rotate(-rotate)

    image.paste(sprite, (x * conf.settings.CELL_SIZE, y * conf.settings.CELL_SIZE), sprite)


def old_draw_sprite(image, texture, sprite_name, x, y, rotate=0, base=False):
    sprite_info = getattr(relations.SPRITES, sprite_name)

    if isinstance(sprite_info, str):
        sprite_info = getattr(relations.SPRITES, sprite_info)

    if base:
        sprite_info = getattr(relations.SPRITES, sprite_info.base)

    sprite_borders = (sprite_info.x, sprite_info.y,
                      sprite_info.x + conf.settings.CELL_SIZE, sprite_info.y + conf.settings.CELL_SIZE)

    sprite = texture.crop(sprite_borders)

    if rotate:
        sprite = sprite.rotate(-rotate)

    image.paste(sprite, (x * conf.settings.CELL_SIZE, y * conf.settings.CELL_SIZE), sprite)


def old_get_roads_map(w, h, roads, places):

    m = []

    for i in range(h):
        m.append([])
        for j in range(w):
            m[-1].append({})

    for road in roads:
        if not road['exists']:
            continue

        point_1 = places[road['point_1_id']]
        pos = point_1['pos']
        x = pos['x']
        y = pos['y']

        for path in road['path']:
            m[y][x][path] = True
            m[y][x]['road'] = True

            if path == 'l':
                x -= 1
            elif path == 'r':
                x += 1
            elif path == 'u':
                y -= 1
            elif path == 'd':
                y += 1

            m[y][x]['road'] = True

    return m


def old_get_road_sprite_info(m, x, y):
    l = 0
    r = 0
    u = 0
    d = 0

    cell = m[y][x]

    l_cell = m[y][x - 1] if x > 0 else {}
    r_cell = m[y][x + 1] if x < len(m[y]) - 1 else {}
    u_cell = m[y - 1][x] if y > 0 else {}
    d_cell = m[y + 1][x] if y < len(m) - 1 else {}

    if cell.get('l') or l_cell.get('r'):
        l = 1
    if cell.get('r') or r_cell.get('l'):
        r = 1
    if cell.get('u') or u_cell.get('d'):
        u = 1
    if cell.get('d') or d_cell.get('u'):
        d = 1

    sum = l + r + u + d

    if sum == 4:
        return {'name': 'R4', 'rotate': 0}

    if sum == 3:
        if not l:
            return {'name': 'R3', 'rotate': 90}
        if not r:
            return {'name': 'R3', 'rotate': 270}
        if not u:
            return {'name': 'R3', 'rotate': 180}
        if not d:
            return {'name': 'R3', 'rotate': 0}

    if l and u:
        return {'name': 'R_ANGLE', 'rotate': 0}
    if l and r:
        return {'name': 'R_HORIZ', 'rotate': 0}
    if l and d:
        return {'name': 'R_ANGLE', 'rotate': 270}

    if u and r:
        return {'name': 'R_ANGLE', 'rotate': 90}
    if u and d:
        return {'name': 'R_VERT', 'rotate': 0}

    if r and d:
        return {'name': 'R_ANGLE', 'rotate': 180}

    if l:
        return {'name': 'R1', 'rotate': 180}
    if r:
        return {'name': 'R1', 'rotate': 0}
    if u:
        return {'name': 'R1', 'rotate': 270}
    if d:
        return {'name': 'R1', 'rotate': 90}


def old_draw(data, output_file_name):

    terrain = data['terrain']
    buildings = list(data['buildings'].values())
    places = list(data['places'].values())
    roads = list(data['roads'].values())

    width = data['width']
    height = data['height']

    roads_map = old_get_roads_map(width, height, roads, {place['id']: place for place in places})

    image = PIL.Image.new('RGBA', (width * conf.settings.CELL_SIZE, height * conf.settings.CELL_SIZE))

    texture = PIL.Image.open(os.path.join(django_settings.PROJECT_DIR, './static/game/images/map.png'))

    for y, row in enumerate(terrain):
        for x, cell in enumerate(row):
            terrain_type = relations.TERRAIN(cell)
            old_draw_sprite(image, texture, terrain_type.name, x, y)

            if roads_map[y][x]:
                old_draw_sprite(image, texture, terrain_type.name, x, y, base=True)

                road_sprite = old_get_road_sprite_info(roads_map, x, y)
                old_draw_sprite(image, texture, road_sprite['name'], x, y, rotate=road_sprite['rotate'])

    for place_info in places:
        size = place_info['size']
        race = game_relations.RACE(place_info['race'])

        if size < 3:
            verbose_size = 'small'
        elif size < 6:
            verbose_size = 'medium'
        elif size < 9:
            verbose_size = 'large'
        else:
            verbose_size = 'capital'

        sprite_name = ('city_%s_%s' % (race.name.lower(), verbose_size)).upper()
        old_draw_sprite(image, texture, sprite_name, place_info['pos']['x'], place_info['pos']['y'])

    for building_info in buildings:
        x, y = building_info['pos']['x'], building_info['pos']['y']
        old_draw_sprite(image, texture, relations.TERRAIN(terrain[y][x]).name, x, y, base=True)

        sprite_name = 'BUILDING_%s' % places_relations.BUILDING_TYPE(building_info['type']).name
        old_draw_sprite(image, texture, sprite_name, x, y)

    image.crop(OUTPUT_RECTANGLE).resize(REAL_SIZE, PIL.Image.ANTIALIAS).save(output_file_name)


def draw(data, output_file_name):

    format_version = data.get('format_version')

    if format_version is None:
        return old_draw(data, output_file_name)

    draw_info = data['draw_info']

    width = data['width']
    height = data['height']

    image = PIL.Image.new('RGBA', (width * conf.settings.CELL_SIZE, height * conf.settings.CELL_SIZE))

    texture = PIL.Image.open(os.path.join(django_settings.PROJECT_DIR, './static/game/images/map.png'))

    for y, row in enumerate(draw_info):
        for x, cell in enumerate(row):
            sprites = cell if isinstance(cell, list) else [cell]
            for sprite in sprites:
                rotate = 0
                if isinstance(sprite, list):
                    sprite, rotate = sprite
                draw_sprite(image, texture, relations.SPRITES(sprite), x, y, rotate=rotate)

    image.crop(OUTPUT_RECTANGLE).resize(REAL_SIZE, PIL.Image.ANTIALIAS).save(output_file_name)
