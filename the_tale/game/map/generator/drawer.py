# coding: utf-8

from the_tale.game.map.relations import SPRITES
from the_tale.game.map.storage import map_info_storage

from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.map.roads.storage import roads_storage


class CellDrawer(object):
    __slots__ = ('terrain', 'road', 'road_rotate', 'object')

    def __init__(self):
        self.terrain = None
        self.road = None
        self.road_rotate = 0
        self.object = None

    def get_sprites(self):
        sprites = []

        if self.road or self.object:
            sprites.append((SPRITES.index_name[self.terrain.base].value, 0))
        else:
            sprites.append((self.terrain.value, 0))

        if self.road is not None:
            sprites.append((self.road.value, self.road_rotate))

        if self.object is not None:
            sprites.append((self.object.value, 0))

        return sprites


def get_roads_map(w, h, roads):

    m = []

    for i in xrange(h):
        m.append([])
        for j in xrange(w):
            m[-1].append({})

    for road in roads:
        if not road.exists: continue

        point_1 = road.point_1
        x = point_1.x
        y = point_1.y

        for path in road.path:
            m[y][x][path] = True
            m[y][x]['road'] = True

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

    cell = m[y][x]

    l_cell = m[y][x-1] if x > 0 else {}
    r_cell = m[y][x+1] if x < len(m[y])-1 else {}
    u_cell = m[y-1][x] if y > 0 else {}
    d_cell = m[y+1][x] if y < len(m)-1 else {}

    if cell.get('l') or l_cell.get('r'): l = 1
    if cell.get('r') or r_cell.get('l'): r = 1
    if cell.get('u') or u_cell.get('d'): u = 1
    if cell.get('d') or d_cell.get('u'): d = 1

    sum = l + r + u + d

    if sum == 4: return {'name': 'R4', 'rotate': 0}

    if sum==3:
        if not l: return {'name': 'R3', 'rotate': 90}
        if not r: return {'name': 'R3', 'rotate': 270}
        if not u: return {'name': 'R3', 'rotate': 180}
        if not d: return {'name': 'R3', 'rotate': 0}

    if l and u: return {'name': 'R_ANGLE', 'rotate': 0}
    if l and r: return {'name': 'R_HORIZ', 'rotate': 0}
    if l and d: return {'name': 'R_ANGLE', 'rotate': 270}

    if u and r: return {'name': 'R_ANGLE', 'rotate': 90}
    if u and d: return {'name': 'R_VERT', 'rotate': 0}

    if r and d: return {'name': 'R_ANGLE', 'rotate': 180}

    if l: return {'name': 'R1', 'rotate': 180}
    if r: return {'name': 'R1', 'rotate': 0}
    if u: return {'name': 'R1', 'rotate': 270}
    if d: return {'name': 'R1', 'rotate': 90}



def get_hero_sprite(hero):
    return SPRITES.index_name[('HERO_%s_%s' % (hero.race.name, hero.gender.name)).upper()]


def get_draw_info(biomes_map):

    width = map_info_storage.item.width
    height = map_info_storage.item.height

    map_images = []
    for y in xrange(height):
        map_images.append([])
        for x in xrange(width):
            map_images[-1].append(CellDrawer())


    roads_map = get_roads_map(width, height, roads_storage.all())

    for y in xrange(height):
        for x in xrange(width):
            biom = biomes_map[y][x]
            cell_drawer = map_images[y][x]

            cell_drawer.terrain = SPRITES.index_name[biom.id.name]

            if roads_map[y][x]:
                road_sprite = get_road_sprite_info(roads_map, x, y)

                cell_drawer.road = SPRITES.index_name[road_sprite['name']]
                cell_drawer.road_rotate = road_sprite['rotate']

    for place in places_storage.all():
        if place.size < 3: verbose_size = 'small'
        elif place.size < 6: verbose_size = 'medium'
        elif place.size < 9: verbose_size = 'large'
        else: verbose_size = 'capital'

        sprite_name = ('city_%s_%s' % (place.race.name.lower(), verbose_size)).upper()

        cell_drawer = map_images[place.y][place.x]
        cell_drawer.object = SPRITES.index_name[sprite_name]

    for building in buildings_storage.all():
        sprite_name = 'BUILDING_%s' % building.type.name

        cell_drawer = map_images[building.y][building.x]
        cell_drawer.object = SPRITES.index_name[sprite_name]

    return map_images
