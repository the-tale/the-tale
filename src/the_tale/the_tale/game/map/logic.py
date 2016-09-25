# coding: utf-8

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from the_tale.game.map.conf import map_settings

from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
from the_tale.linguistics.storage import restrictions_storage


def create_test_map_info():
    map_info_storage.set_item(MapInfoPrototype.create(turn_number=0,
                                                      width=map_settings.WIDTH,
                                                      height=map_settings.HEIGHT,
                                                      terrain=[ [TERRAIN.PLANE_GREENWOOD for j in xrange(map_settings.WIDTH)] for i in xrange(map_settings.HEIGHT)], # pylint: disable=W0612
                                                      world=WorldInfoPrototype.create(w=map_settings.WIDTH, h=map_settings.HEIGHT)))


_TERRAIN_LINGUISTICS_CACHE = {}

def get_terrain_linguistics_restrictions(terrain):

    if _TERRAIN_LINGUISTICS_CACHE:
        return _TERRAIN_LINGUISTICS_CACHE[terrain]

    for terrain_record in TERRAIN.records:
        _TERRAIN_LINGUISTICS_CACHE[terrain_record] = ( restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.TERRAIN, terrain_record.value).id,
                                                       restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_TERRAIN, terrain_record.meta_terrain.value).id,
                                                       restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_HEIGHT, terrain_record.meta_height.value).id,
                                                       restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_VEGETATION, terrain_record.meta_vegetation.value).id )

    return _TERRAIN_LINGUISTICS_CACHE[terrain]
