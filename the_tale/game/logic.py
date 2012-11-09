# coding: utf-8
import os

from django.conf import settings as project_settings

from textgen import words
from dext.utils import s11n

from game.heroes.bag import SLOTS
from game.artifacts.storage import ArtifactsDatabase
from game.bundles import BundlePrototype

from game.map.storage import map_info_storage
from game.persons.storage import persons_storage
from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage, waymarks_storage


from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.logic import update_waymarks
from game.map.prototypes import MapInfoPrototype
from game.map.places.logic import update_nearest_cells
from game.map.conf import map_settings


def create_test_map():
    places_storage.clear()
    persons_storage.clear()
    roads_storage.clear()

    """
    map: p1-p2-p3
    """
    p1 = Place.objects.create( x=1,
                               y=1,
                               name='1x1',
                               name_forms=s11n.to_json(words.Noun('1x1').serialize()),
                               terrain=TERRAIN.FOREST,
                               type=PLACE_TYPE.CITY,
                               subtype='UNDEFINED',
                               size=1)

    p2 = Place.objects.create( x=10,
                               y=10,
                               name='10x10',
                               name_forms=s11n.to_json(words.Noun('10x10').serialize()),
                               terrain=TERRAIN.FOREST,
                               type=PLACE_TYPE.CITY,
                               subtype='UNDEFINED',
                               size=3)

    p3 = Place.objects.create( x=1,
                               y=10,
                               name='1x10',
                               name_forms=s11n.to_json(words.Noun('1x10').serialize()),
                               terrain=TERRAIN.FOREST,
                               type=PLACE_TYPE.CITY,
                               subtype='UNDEFINED',
                               size=3)

    places_storage.sync(force=True)

    for place in places_storage.all():
        place.sync_persons()

    persons_storage.sync(force=True)

    RoadPrototype.create(point_1=places_storage[p1.id], point_2=places_storage[p2.id])
    RoadPrototype.create(point_1=places_storage[p2.id], point_2=places_storage[p3.id])

    update_waymarks()

    waymarks_storage.sync(force=True)

    roads_storage.sync(force=True)

    map_info_storage.set_item(MapInfoPrototype.create(turn_number=0,
                                                      width=map_settings.WIDTH,
                                                      height=map_settings.HEIGHT,
                                                      terrain=[ [TERRAIN.FOREST for j in xrange(map_settings.WIDTH)] for j in xrange(map_settings.HEIGHT)]))

    update_nearest_cells()

    return (places_storage[p1.id], places_storage[p2.id], places_storage[p3.id])


def create_test_bundle(uuid):
    from accounts.logic import register_user
    result, account_id, bundle_id = register_user(uuid, uuid + '@test.com', '111111')
    return BundlePrototype.get_by_id(bundle_id)


def dress_new_hero(hero):
    storage = ArtifactsDatabase.storage()

    hero.equipment.equip(SLOTS.PANTS, storage.create_artifact('default_pants', level=1, power=0))
    hero.equipment.equip(SLOTS.BOOTS, storage.create_artifact('default_boots', level=1, power=0))
    hero.equipment.equip(SLOTS.PLATE, storage.create_artifact('default_plate', level=1, power=0))
    hero.equipment.equip(SLOTS.GLOVES, storage.create_artifact('default_gloves', level=1, power=0))
    hero.equipment.equip(SLOTS.HAND_PRIMARY, storage.create_artifact('default_weapon', level=1, power=0))


def log_sql_queries(turn_number):
    from django.db import connection

    with open(os.path.join(project_settings.DEBUG_DATABASE_USAGE_OUTPUT_DIR, '%d.turn' % turn_number), 'w') as f:
        f.write('total queries: %d\n\n' % len(connection.queries))
        for querie in connection.queries:
            f.write('%s\t %s\n\n' % (querie['time'], querie['sql']))

    connection.queries = []
