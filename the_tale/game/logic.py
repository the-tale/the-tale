# coding: utf-8
import os
import time
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.accounts.conf import accounts_settings

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game import names
from the_tale.game import conf

from the_tale.game.prototypes import TimePrototype

from the_tale.game.persons.storage import persons_storage

from the_tale.game.mobs.prototypes import MobRecordPrototype
from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import ARTIFACT_TYPE

from the_tale.game.cards import container as cards_container

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map import logic as map_logic

from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.map.places.prototypes import PlacePrototype
from the_tale.game.map.places.logic import update_nearest_cells

from the_tale.game.map.roads.storage import roads_storage, waymarks_storage
from the_tale.game.map.roads.prototypes import RoadPrototype
from the_tale.game.map.roads.logic import update_waymarks

from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.heroes import objects as heroes_objects


@places_storage.postpone_version_update
@buildings_storage.postpone_version_update
@persons_storage.postpone_version_update
@waymarks_storage.postpone_version_update
@roads_storage.postpone_version_update
@mobs_storage.postpone_version_update
@artifacts_storage.postpone_version_update
def create_test_map():
    linguistics_logic.sync_static_restrictions()

    map_logic.create_test_my_info()

    p1 = PlacePrototype.create( x=1, y=1, size=1, utg_name=names.generator.get_test_name(name='1x1'))
    p2 = PlacePrototype.create( x=3, y=3, size=3, utg_name=names.generator.get_test_name(name='10x10'))
    p3 = PlacePrototype.create( x=1, y=3, size=3, utg_name=names.generator.get_test_name(name='1x10'))

    for place in places_storage.all():
        place.sync_persons(force_add=True)

    RoadPrototype.create(point_1=p1, point_2=p2).update()
    RoadPrototype.create(point_1=p2, point_2=p3).update()

    update_waymarks()

    update_nearest_cells()

    mob_1 = MobRecordPrototype.create_random('mob_1')
    mob_2 = MobRecordPrototype.create_random('mob_2')
    mob_3 = MobRecordPrototype.create_random('mob_3')

    ArtifactRecordPrototype.create_random('loot_1', mob=mob_1)
    ArtifactRecordPrototype.create_random('loot_2', mob=mob_2)
    ArtifactRecordPrototype.create_random('loot_3', mob=mob_3)

    ArtifactRecordPrototype.create_random('helmet_1', type_=ARTIFACT_TYPE.HELMET, mob=mob_1)
    ArtifactRecordPrototype.create_random('plate_1', type_=ARTIFACT_TYPE.PLATE, mob=mob_2)
    ArtifactRecordPrototype.create_random('boots_1', type_=ARTIFACT_TYPE.BOOTS, mob=mob_3)

    for equipment_slot in heroes_relations.EQUIPMENT_SLOT.records:
        if equipment_slot.default:
            ArtifactRecordPrototype.create_random(equipment_slot.default, type_=equipment_slot.artifact_type)

    companions_logic.create_random_companion_record('companion_1', dedication=companions_relations.DEDICATION.HEROIC, state=companions_relations.STATE.ENABLED)
    companions_logic.create_random_companion_record('companion_2', dedication=companions_relations.DEDICATION.BOLD, state=companions_relations.STATE.ENABLED)
    companions_logic.create_random_companion_record('companion_3', dedication=companions_relations.DEDICATION.BOLD, state=companions_relations.STATE.DISABLED)

    return p1, p2, p3


def log_sql_queries(turn_number):
    from django.db import connection

    with open(os.path.join('/tmp/', '%d.turn' % turn_number), 'w') as f:
        f.write('total queries: %d\n\n' % len(connection.queries))
        for querie in connection.queries:
            f.write('%s\t %s\n\n' % (querie['time'], querie['sql']))

    connection.queries = []


def remove_game_data(account):
    heroes_logic.remove_hero(account_id=account.id)


def _form_game_account_info(game_time, account, in_pvp_queue, is_own, client_turns=None):
    data = { 'new_messages': account.new_messages_number if is_own else 0,
             'id': account.id,
             'last_visit': time.mktime((account.active_end_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)).timetuple()),
             'is_own': is_own,
             'is_old': False,
             'hero': None,
             'in_pvp_queue': in_pvp_queue }

    hero_data = heroes_objects.Hero.cached_ui_info_for_hero(account_id=account.id,
                                                      recache_if_required=is_own,
                                                      patch_turns=client_turns,
                                                      for_last_turn=(not is_own))
    data['hero'] = hero_data

    data['is_old'] = (data['hero']['actual_on_turn'] < game_time.turn_number)

    if not is_own:
        if 'cards' in hero_data:
            hero_data['cards'] = cards_container.CardsContainer.ui_info_null()
        if 'energy' in hero_data:
            hero_data['energy']['max'] = 0
            hero_data['energy']['value'] = 0
            hero_data['energy']['bonus'] = 0
            hero_data['energy']['discount'] = 0

    return data


def form_game_info(account=None, is_own=False, client_turns=None):
    from the_tale.accounts.prototypes import AccountPrototype
    from the_tale.game.prototypes import GameState
    from the_tale.game.pvp.prototypes import Battle1x1Prototype

    game_time = TimePrototype.get_current_time()

    data = {'mode': 'pve',
            'turn': game_time.ui_info(),
            'game_state': GameState.state().value,
            'map_version': map_info_storage.version,
            'account': None,
            'enemy': None }

    if account:
        battle = Battle1x1Prototype.get_by_account_id(account.id)
        data['account'] = _form_game_account_info(game_time,
                                                  account,
                                                  in_pvp_queue=False if battle is None else battle.state.is_WAITING,
                                                  is_own=is_own,
                                                  client_turns=client_turns)

        if battle and battle.state.is_PROCESSING:
            data['mode'] = 'pvp'
            data['enemy'] = _form_game_account_info(game_time,
                                                    AccountPrototype.get_by_id(battle.enemy_id),
                                                    in_pvp_queue=False,
                                                    is_own=False,
                                                    client_turns=client_turns)

    return data


def game_info_url(account_id=None, client_turns=None):
    arguments = {'api_version': conf.game_settings.INFO_API_VERSION,
                 'api_client': project_settings.API_CLIENT}

    if account_id is not None:
        arguments['account'] = account_id

    if client_turns:
        arguments['client_turns'] = ','.join(str(turn) for turn in client_turns)

    return url('game:api-info', **arguments)


def _game_info_from_1_1_to_1_0__heroes(data):
    data['secondary']['power'] = sum(data['secondary']['power'])

    for artifact in data['equipment'].values():
        artifact['power'] = sum(artifact['power']) if artifact['power'] else 0

    for artifact in data['bag'].values():
        artifact['power'] = sum(artifact['power']) if artifact['power'] else 0


def _game_info_from_1_3_to_1_2__heroes(data):
    if 'diary' in data:
        data['diary'] = [message[:4] for message in data['diary']]


def _game_info_from_1_2_to_1_1__heroes(data):
    data['secondary']['cards_help_count'] = 0
    data['secondary']['cards_help_barrier'] = data['cards']['help_barrier']
    data['cards'] = {'cards': {}}


def _remove_variables_from_message(message):
    return message[:3] + message[5:]

def _game_info_from_1_4_to_1_3__heroes(data):
    if 'diary' in data:
        data['diary'] = [_remove_variables_from_message(message) for message in data['diary']]

    if 'messages' in data:
        data['messages'] = [_remove_variables_from_message(message) for message in data['messages']]


def game_info_from_1_1_to_1_0(data):
    if data['account'] is not None:
        _game_info_from_1_1_to_1_0__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_1_to_1_0__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_2_to_1_1(data):
    if data['account'] is not None:
        _game_info_from_1_2_to_1_1__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_2_to_1_1__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_3_to_1_2(data):
    if data['account'] is not None:
        _game_info_from_1_3_to_1_2__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_3_to_1_2__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_4_to_1_3(data):
    if data['account'] is not None:
        _game_info_from_1_4_to_1_3__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_4_to_1_3__heroes(data['enemy']['hero'])

    return data
