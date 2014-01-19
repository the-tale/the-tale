# coding: utf-8

import json

import PIL

from optparse import make_option

from django.core.management.base import BaseCommand

from the_tale.game.relations import RACE

from the_tale.game.map.places.relations import BUILDING_TYPE

from the_tale.game.map.relations import TERRAIN, SPRITES
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.conf import map_settings


OUTPUT_RECTANGLE = (8*map_settings.CELL_SIZE, 1*map_settings.CELL_SIZE, 50*map_settings.CELL_SIZE, 36*map_settings.CELL_SIZE)

REAL_SIZE = ((OUTPUT_RECTANGLE[2]-OUTPUT_RECTANGLE[0]),
             (OUTPUT_RECTANGLE[3]-OUTPUT_RECTANGLE[1]))


def draw_sprite(image, texture, sprite_name, x, y, rotate=0, base=False):
    sprite_info = SPRITES.index_name[sprite_name]

    if isinstance(sprite_info, basestring):
        sprite_info = SPRITES.index_name[sprite_info]

    if base:
        sprite_info = SPRITES.index_name[sprite_info.base]

    sprite_borders = (sprite_info.x, sprite_info.y,
                      sprite_info.x + map_settings.CELL_SIZE, sprite_info.y + map_settings.CELL_SIZE)

    sprite = texture.crop(sprite_borders)

    if rotate:
        sprite = sprite.rotate(-rotate)

    image.paste(sprite, (x * map_settings.CELL_SIZE, y * map_settings.CELL_SIZE), sprite)


def get_roads_map(w, h, roads, places):

    m = []

    for i in xrange(h):
        m.append([])
        for j in xrange(w):
            m[-1].append({})

    for road in roads:
        if not road['exists']: continue

        point_1 = places[road['point_1_id']];
        pos = point_1['pos'];
        x = pos['x'];
        y = pos['y'];

        for path in road['path']:
            m[y][x][path] = True;
            m[y][x]['road'] = True;

            if path == 'l': x -= 1
            elif path == 'r': x += 1
            elif path == 'u': y -= 1
            elif path == 'd': y += 1

            m[y][x]['road'] = True

    return m

def get_road_sprite_info(m, x, y):
    l = 0
    r = 0
    u = 0
    d = 0

    cell = m[y][x];

    l_cell = m[y][x-1] if x > 0 else {}
    r_cell = m[y][x+1] if x < len(m[y])-1 else {}
    u_cell = m[y-1][x] if y > 0 else {}
    d_cell = m[y+1][x] if y < len(m)-1 else {};

    if cell.get('l') or l_cell.get('r'): l = 1
    if cell.get('r') or r_cell.get('l'): r = 1
    if cell.get('u') or u_cell.get('d'): u = 1
    if cell.get('d') or d_cell.get('u'): d = 1

    sum = l + r + u + d

    if sum == 4: return {'name': 'R4', 'rotate': 0}

    if sum==3:
        if not l: return {'name': 'R3', 'rotate': 90};
        if not r: return {'name': 'R3', 'rotate': 270};
        if not u: return {'name': 'R3', 'rotate': 180};
        if not d: return {'name': 'R3', 'rotate': 0};

    if l and u: return {'name': 'R_ANGLE', 'rotate': 0};
    if l and r: return {'name': 'R_HORIZ', 'rotate': 0};
    if l and d: return {'name': 'R_ANGLE', 'rotate': 270};

    if u and r: return {'name': 'R_ANGLE', 'rotate': 90};
    if u and d: return {'name': 'R_VERT', 'rotate': 0};

    if r and d: return {'name': 'R_ANGLE', 'rotate': 180};

    if l: return {'name': 'R1', 'rotate': 180};
    if r: return {'name': 'R1', 'rotate': 0};
    if u: return {'name': 'R1', 'rotate': 270};
    if d: return {'name': 'R1', 'rotate': 90};




class Command(BaseCommand):

    help = 'visualize map with region data'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-r', '--region',
                                                          action='store',
                                                          type=str,
                                                          dest='region',
                                                          help='region file name'),
                                              make_option('-o', '--output',
                                                          action='store',
                                                          type=str,
                                                          dest='output',
                                                          help='output file'),)


    def handle(self, *args, **options):

        region = options['region']
        if not region:
            region = map_settings.GEN_REGION_OUTPUT % map_info_storage.version

        output = options['output']
        if not output:
            output = '/tmp/the-tale-map.png'

        with open(region) as region_file:
            data = json.loads(region_file.read())

        terrain = data['terrain']
        buildings = data['buildings'].values()
        places = data['places'].values()
        roads = data['roads'].values()

        width = data['width']
        height = data['height']

        roads_map = get_roads_map(width, height, roads, {place['id']:place for place in places})

        image = PIL.Image.new('RGBA', (width*map_settings.CELL_SIZE, height*map_settings.CELL_SIZE))

        texture = PIL.Image.open(map_settings.TEXTURE_PATH)

        for y, row in enumerate(terrain):
            for x, cell in enumerate(row):
                terrain_type = TERRAIN(cell)
                draw_sprite(image, texture, terrain_type.name, x, y)

                if roads_map[y][x]:
                    draw_sprite(image, texture, terrain_type.name, x, y, base=True)

                    road_sprite = get_road_sprite_info(roads_map, x, y)
                    draw_sprite(image, texture, road_sprite['name'], x, y, rotate=road_sprite['rotate'])

        for place_info in places:
            size = place_info['size']
            race = RACE(place_info['race'])

            if size < 3: verbose_size = 'small'
            elif size < 6: verbose_size = 'medium'
            elif size < 9: verbose_size = 'large'
            else: verbose_size = 'capital'

            sprite_name = ('city_%s_%s' % (race.name.lower(), verbose_size)).upper()
            draw_sprite(image, texture, sprite_name, place_info['pos']['x'], place_info['pos']['y'])

        for building_info in buildings:
            x, y = building_info['pos']['x'], building_info['pos']['y']
            draw_sprite(image, texture, TERRAIN(terrain[y][x]).name, x, y, base=True)

            sprite_name = 'BUILDING_%s' % BUILDING_TYPE(building_info['type']).name
            draw_sprite(image, texture, sprite_name, x, y)

        image.crop(OUTPUT_RECTANGLE).resize(REAL_SIZE, PIL.Image.ANTIALIAS).save(output)
