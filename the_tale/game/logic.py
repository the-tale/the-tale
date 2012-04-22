# coding: utf-8

from django.contrib.auth.models import User

from accounts.prototypes import AccountPrototype

from game.angels.prototypes import AngelPrototype
from game.heroes.prototypes import HeroPrototype
from game.bundles import BundlePrototype

from game.map.places.prototypes import get_place_by_model
from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.logic import update_waymarks
from game.map.prototypes import MapInfoPrototype
from game.map.places.logic import update_nearest_cells
from game.map.conf import map_settings

def create_test_map():
    p1 = get_place_by_model(Place.objects.create( x=1,
                                                  y=1,
                                                  name='1x1',
                                                  terrain=TERRAIN.FOREST,
                                                  type=PLACE_TYPE.CITY,
                                                  subtype='UNDEFINED',
                                                  size=1))

    p1.sync_persons()

    p2 = get_place_by_model(Place.objects.create( x=10,
                                                  y=10,
                                                  name='10x10',
                                                  terrain=TERRAIN.FOREST,
                                                  type=PLACE_TYPE.CITY,
                                                  subtype='UNDEFINED',
                                                  size=3))
    p2.sync_persons()

    RoadPrototype.create(point_1=p1, point_2=p2)

    update_waymarks()
    # WaymarkPrototype.create(p1, p2, r1_2, 10)
    # WaymarkPrototype.create(p2, p1, r1_2, 10)

    MapInfoPrototype.create(turn_number=0,
                            width=map_settings.WIDTH,
                            height=map_settings.HEIGHT,
                            terrain=[ [TERRAIN.FOREST for j in xrange(map_settings.WIDTH)] for j in xrange(map_settings.HEIGHT)])

    update_nearest_cells()


def create_test_bundle(uuid):
    user = User.objects.create_user(uuid,
                                    uuid + '@' + uuid + '.com',
                                    '111111')

    account = AccountPrototype.create(user=user)
    angel = AngelPrototype.create(account=account, name=user.username)
    HeroPrototype.create(angel=angel)

    return BundlePrototype.create(angel)
