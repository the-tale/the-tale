# coding: utf-8

from django.contrib.auth.models import User

from accounts.prototypes import AccountPrototype

from game.angels.prototypes import AngelPrototype
from game.heroes.prototypes import HeroPrototype
from game.bundles import BundlePrototype

from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.roads.models import Road

def create_test_map():
    p1 = Place.objects.create( x=1,
                               y=1,
                               name='1x1',
                               terrain=TERRAIN.FOREST,
                               type=PLACE_TYPE.CITY,
                               subtype='UNDEFINED',
                               size=1)

    p2 = Place.objects.create( x=10,
                               y=10,
                               name='10x10',
                               terrain=TERRAIN.GRASS,
                               type=PLACE_TYPE.CITY,
                               subtype='UNDEFINED',
                               size=3)

    Road.objects.create(point_1=p1, point_2=p2)


def create_test_bundle(uuid):
    user = User.objects.create_user(uuid,
                                    uuid + '@' + uuid + '.com',
                                    '111111')

    account = AccountPrototype.create(user=user)
    angel = AngelPrototype.create(account=account, name=user.username)
    HeroPrototype.create(angel=angel)

    return BundlePrototype.create(angel)
