# coding: utf-8
import os

from django.conf import settings as project_settings

from dext.utils.urls import url

from textgen import words

from common.utils.enum import create_enum

from game.prototypes import TimePrototype

from game.heroes.relations import EQUIPMENT_SLOT

from game.persons.storage import persons_storage

from game.mobs.prototypes import MobRecordPrototype
from game.mobs.storage import mobs_storage

from game.artifacts.prototypes import ArtifactRecordPrototype
from game.artifacts.storage import artifacts_storage
from game.artifacts.models import ARTIFACT_TYPE

from game.map.storage import map_info_storage
from game.map.relations import TERRAIN
from game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from game.map.conf import map_settings

from game.map.places.storage import places_storage, buildings_storage
from game.map.places.prototypes import PlacePrototype
from game.map.places.logic import update_nearest_cells

from game.map.roads.storage import roads_storage, waymarks_storage
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.logic import update_waymarks


DEFAULT_HERO_EQUIPMENT = create_enum('DEFAULT_HERO_EQUIPMENT', ( ('PANTS', 'default_pants', u'штаны'),
                                                                 ('BOOTS', 'default_boots', u'обувь'),
                                                                 ('PLATE', 'default_plate', u'доспех'),
                                                                 ('GLOVES', 'default_gloves', u'перчатки'),
                                                                 ('WEAPON', 'default_weapon', u'оружие') ))


@places_storage.postpone_version_update
@buildings_storage.postpone_version_update
@persons_storage.postpone_version_update
@waymarks_storage.postpone_version_update
@roads_storage.postpone_version_update
@mobs_storage.postpone_version_update
@artifacts_storage.postpone_version_update
def create_test_map():
    p1 = PlacePrototype.create( x=1, y=1, size=1, name_forms=words.Noun.fast_construct('1x1'))
    p2 = PlacePrototype.create( x=3, y=3, size=3, name_forms=words.Noun.fast_construct('10x10'))
    p3 = PlacePrototype.create( x=1, y=3, size=3, name_forms=words.Noun.fast_construct('1x10'))

    for place in places_storage.all():
        place.sync_persons()

    RoadPrototype.create(point_1=p1, point_2=p2)
    RoadPrototype.create(point_1=p2, point_2=p3)

    update_waymarks()

    map_info_storage.set_item(MapInfoPrototype.create(turn_number=0,
                                                      width=map_settings.WIDTH,
                                                      height=map_settings.HEIGHT,
                                                      terrain=[ [TERRAIN.PLANE_GREENWOOD for j in xrange(map_settings.WIDTH)] for i in xrange(map_settings.HEIGHT)], # pylint: disable=W0612
                                                      world=WorldInfoPrototype.create(w=map_settings.WIDTH, h=map_settings.HEIGHT)))

    update_nearest_cells()

    mob_1 = MobRecordPrototype.create_random('mob_1')
    mob_2 = MobRecordPrototype.create_random('mob_2')
    mob_3 = MobRecordPrototype.create_random('mob_3')

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

    return p1, p2, p3


def dress_new_hero(hero):
    hero.equipment.equip(EQUIPMENT_SLOT.PANTS, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.PANTS).create_artifact(level=1, power=0))
    hero.equipment.equip(EQUIPMENT_SLOT.BOOTS, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.BOOTS).create_artifact(level=1, power=0))
    hero.equipment.equip(EQUIPMENT_SLOT.PLATE, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.PLATE).create_artifact(level=1, power=0))
    hero.equipment.equip(EQUIPMENT_SLOT.GLOVES, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.GLOVES).create_artifact(level=1, power=0))
    hero.equipment.equip(EQUIPMENT_SLOT.HAND_PRIMARY, artifacts_storage.get_by_uuid(DEFAULT_HERO_EQUIPMENT.WEAPON).create_artifact(level=1, power=0))


def log_sql_queries(turn_number):
    from django.db import connection

    with open(os.path.join(project_settings.DEBUG_DATABASE_USAGE_OUTPUT_DIR, '%d.turn' % turn_number), 'w') as f:
        f.write('total queries: %d\n\n' % len(connection.queries))
        for querie in connection.queries:
            f.write('%s\t %s\n\n' % (querie['time'], querie['sql']))

    connection.queries = []


def remove_game_data(account):
    from game.logic_storage import LogicStorage
    from game.bundles import BundlePrototype

    bundle = BundlePrototype.get_by_account_id(account.id)

    storage = LogicStorage()
    storage.load_account_data(account)
    storage._destroy_account_data(account)

    bundle.remove()

def _form_game_account_info(game_time, account, in_pvp_queue):
    from game.heroes.prototypes import HeroPrototype

    is_own = account.is_authenticated()

    data = { 'new_messages': account.new_messages_number if is_own else 0,
             'id': account.id,
             'is_own': is_own,
             'is_old': False,
             'hero': None,
             'in_pvp_queue': in_pvp_queue }

    if is_own:
        data['hero'] = HeroPrototype.cached_ui_info_for_hero(account.id)
    else:
        data['hero'] = HeroPrototype.get_by_account_id(account.id).ui_info(for_last_turn=True)

    data['is_old'] = (data['hero']['saved_at_turn'] < game_time.turn_number)

    return data


def form_game_info(account=None):
    from accounts.prototypes import AccountPrototype

    from game.pvp.prototypes import Battle1x1Prototype

    game_time = TimePrototype.get_current_time()

    data = {'mode': 'pve',
            'turn': game_time.ui_info(),
            'map_version': map_info_storage.version,
            'account': None,
            'enemy': None }

    if account:
        battle = Battle1x1Prototype.get_by_account_id(account.id)
        data['account'] = _form_game_account_info(game_time, account, in_pvp_queue=False if battle is None else battle.state._is_WAITING)

        if battle and (battle.state._is_PROCESSING or battle.state._is_PREPAIRING):
            data['mode'] = 'pvp'
            data['enemy'] = _form_game_account_info(game_time, AccountPrototype.get_by_id(battle.enemy_id), in_pvp_queue=False)

    return data


def game_info_url(account_id=None):
    if account_id is not None:
        return url('game:api-info', account=account_id, api_version='1.0', api_client=project_settings.API_CLIENT)
    return url('game:api-info', api_version='1.0', api_client=project_settings.API_CLIENT)
