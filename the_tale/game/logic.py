# coding: utf-8
import os

from django.conf import settings as project_settings

from textgen import words
from dext.utils import s11n

from common.utils.enum import create_enum

from game.heroes.bag import SLOTS
from game.bundles import BundlePrototype

from game.persons.storage import persons_storage

from game.mobs.prototypes import MobRecordPrototype
from game.mobs.storage import mobs_storage

from game.artifacts.prototypes import ArtifactRecordPrototype
from game.artifacts.storage import artifacts_storage
from game.artifacts.models import ARTIFACT_TYPE

from game.map.storage import map_info_storage
from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage, waymarks_storage
from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.logic import update_waymarks
from game.map.prototypes import MapInfoPrototype
from game.map.places.logic import update_nearest_cells
from game.map.conf import map_settings

DEFAULT_HERO_EQUIPMENT = create_enum('DEFAULT_HERO_EQUIPMENT', ( ('PANTS', 'default_pants', u'штаны'),
                                                                 ('BOOTS', 'default_boots', u'обувь'),
                                                                 ('PLATE', 'default_plate', u'доспех'),
                                                                 ('GLOVES', 'default_gloves', u'перчатки'),
                                                                 ('WEAPON', 'default_weapon', u'оружие') ))


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
                               type=PLACE_TYPE.CITY,
                               size=1)

    p2 = Place.objects.create( x=10,
                               y=10,
                               name='10x10',
                               name_forms=s11n.to_json(words.Noun('10x10').serialize()),
                               type=PLACE_TYPE.CITY,
                               size=3)

    p3 = Place.objects.create( x=1,
                               y=10,
                               name='1x10',
                               name_forms=s11n.to_json(words.Noun('1x10').serialize()),
                               type=PLACE_TYPE.CITY,
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
                                                      terrain=[ [TERRAIN.PLANE_GREENWOOD for j in xrange(map_settings.WIDTH)] for j in xrange(map_settings.HEIGHT)],
                                                      world=MapInfoPrototype._create_world(w=map_settings.WIDTH, h=map_settings.HEIGHT)))

    update_nearest_cells()

    mob_1 = MobRecordPrototype.create_random('mob_1')
    mob_2 = MobRecordPrototype.create_random('mob_2')
    mob_3 = MobRecordPrototype.create_random('mob_3')

    mobs_storage.sync(force=True)

    ArtifactRecordPrototype.create_random('letter') # for delivery quests

    ArtifactRecordPrototype.create_random('loot_1', mob=mob_1)
    ArtifactRecordPrototype.create_random('loot_2', mob=mob_2)
    ArtifactRecordPrototype.create_random('loot_3', mob=mob_3)

    ArtifactRecordPrototype.create_random('helmet_1', type_=ARTIFACT_TYPE.HELMET, mob=mob_1)
    ArtifactRecordPrototype.create_random('plate_1', type_=ARTIFACT_TYPE.PLATE, mob=mob_2)
    ArtifactRecordPrototype.create_random('boots_1', type_=ARTIFACT_TYPE.BOOTS, mob=mob_3)

    ArtifactRecordPrototype.create_random(DEFAULT_HERO_EQUIPMENT.PANTS, type_=ARTIFACT_TYPE.PANTS)
    ArtifactRecordPrototype.create_random(DEFAULT_HERO_EQUIPMENT.BOOTS, type_=ARTIFACT_TYPE.BOOTS)
    ArtifactRecordPrototype.create_random(DEFAULT_HERO_EQUIPMENT.PLATE, type_=ARTIFACT_TYPE.PLATE)
    ArtifactRecordPrototype.create_random(DEFAULT_HERO_EQUIPMENT.GLOVES, type_=ARTIFACT_TYPE.GLOVES)
    ArtifactRecordPrototype.create_random(DEFAULT_HERO_EQUIPMENT.WEAPON, type_=ARTIFACT_TYPE.MAIN_HAND)

    artifacts_storage.sync(force=True)

    return (places_storage[p1.id], places_storage[p2.id], places_storage[p3.id])


def create_test_bundle(uuid):
    from accounts.logic import register_user
    result, account_id, bundle_id = register_user(uuid, uuid + '@test.com', '111111')
    return BundlePrototype.get_by_id(bundle_id)


def dress_new_hero(hero):
    hero.equipment.equip(SLOTS.PANTS, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.PANTS).create_artifact(level=1, power=0))
    hero.equipment.equip(SLOTS.BOOTS, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.BOOTS).create_artifact(level=1, power=0))
    hero.equipment.equip(SLOTS.PLATE, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.PLATE).create_artifact(level=1, power=0))
    hero.equipment.equip(SLOTS.GLOVES, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.GLOVES).create_artifact(level=1, power=0))
    hero.equipment.equip(SLOTS.HAND_PRIMARY, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.WEAPON).create_artifact(level=1, power=0))


def log_sql_queries(turn_number):
    from django.db import connection

    with open(os.path.join(project_settings.DEBUG_DATABASE_USAGE_OUTPUT_DIR, '%d.turn' % turn_number), 'w') as f:
        f.write('total queries: %d\n\n' % len(connection.queries))
        for querie in connection.queries:
            f.write('%s\t %s\n\n' % (querie['time'], querie['sql']))

    connection.queries = []

def clean_database():
    from django.db import models
    from game.models import Bundle

    # remove unused bundles
    Bundle.objects.annotate(actions_number=models.Count('action')).filter(actions_number=0).delete()
