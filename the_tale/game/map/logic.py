# coding: utf-8

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from the_tale.game.map.conf import map_settings



def create_test_my_info():
    map_info_storage.set_item(MapInfoPrototype.create(turn_number=0,
                                                      width=map_settings.WIDTH,
                                                      height=map_settings.HEIGHT,
                                                      terrain=[ [TERRAIN.PLANE_GREENWOOD for j in xrange(map_settings.WIDTH)] for i in xrange(map_settings.HEIGHT)], # pylint: disable=W0612
                                                      world=WorldInfoPrototype.create(w=map_settings.WIDTH, h=map_settings.HEIGHT)))
