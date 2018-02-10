
import os
import time
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.accounts.conf import accounts_settings

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game import names
from the_tale.game import conf
from the_tale.game import turn

from the_tale.game.persons import storage as persons_storage

from the_tale.game.mobs import logic as mobs_logic
from the_tale.game.mobs import storage as mobs_storage

from the_tale.game.artifacts import logic as artifacts_logic
from the_tale.game.artifacts import storage as artifacts_storage
from the_tale.game.artifacts import relations as artifacts_relations

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map import logic as map_logic

from the_tale.game.places import storage as places_storage
from the_tale.game.places import logic as places_logic
from the_tale.game.places import nearest_cells

from the_tale.game.roads.storage import roads_storage, waymarks_storage
from the_tale.game.roads.prototypes import RoadPrototype
from the_tale.game.roads.logic import update_waymarks

from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.heroes import tt_api as heroes_tt_api
from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.heroes import objects as heroes_objects

from . import tt_api
from . import relations


@places_storage.places.postpone_version_update
@places_storage.buildings.postpone_version_update
@persons_storage.persons.postpone_version_update
@waymarks_storage.postpone_version_update
@roads_storage.postpone_version_update
@mobs_storage.mobs.postpone_version_update
@artifacts_storage.artifacts.postpone_version_update
def create_test_map():
    linguistics_logic.sync_static_restrictions()

    map_logic.create_test_map_info()

    p1 = places_logic.create_place( x=1, y=1, size=1, utg_name=names.generator().get_test_name(name='1x1'), race=relations.RACE.HUMAN)
    p2 = places_logic.create_place( x=3, y=3, size=3, utg_name=names.generator().get_test_name(name='10x10'), race=relations.RACE.HUMAN)
    p3 = places_logic.create_place( x=1, y=3, size=3, utg_name=names.generator().get_test_name(name='1x10'), race=relations.RACE.HUMAN)

    for place in places_storage.places.all():
        for i in range(3):
            places_logic.add_person_to_place(place)

    RoadPrototype.create(point_1=p1, point_2=p2).update()
    RoadPrototype.create(point_1=p2, point_2=p3).update()

    update_waymarks()

    nearest_cells.update_nearest_cells()

    mob_1 = mobs_logic.create_random_mob_record('mob_1')
    mob_2 = mobs_logic.create_random_mob_record('mob_2')
    mob_3 = mobs_logic.create_random_mob_record('mob_3')

    artifacts_logic.create_random_artifact_record('loot_1', mob=mob_1)
    artifacts_logic.create_random_artifact_record('loot_2', mob=mob_2)
    artifacts_logic.create_random_artifact_record('loot_3', mob=mob_3)

    artifacts_logic.create_random_artifact_record('helmet_1', type=artifacts_relations.ARTIFACT_TYPE.HELMET, mob=mob_1)
    artifacts_logic.create_random_artifact_record('plate_1', type=artifacts_relations.ARTIFACT_TYPE.PLATE, mob=mob_2)
    artifacts_logic.create_random_artifact_record('boots_1', type=artifacts_relations.ARTIFACT_TYPE.BOOTS, mob=mob_3)

    for equipment_slot in heroes_relations.EQUIPMENT_SLOT.records:
        if equipment_slot.default:
            artifacts_logic.create_random_artifact_record(equipment_slot.default, type=equipment_slot.artifact_type)

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


def _form_game_account_info(turn_number, account, in_pvp_queue, is_own, client_turns=None):
    data = {'id': account.id,
            'last_visit': time.mktime((account.active_end_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)).timetuple()),
            'is_own': is_own,
            'is_old': False,
            'hero': None,
            'in_pvp_queue': in_pvp_queue}

    hero_data = heroes_objects.Hero.cached_ui_info_for_hero(account_id=account.id,
                                                            recache_if_required=is_own,
                                                            patch_turns=client_turns,
                                                            for_last_turn=(not is_own))
    data['hero'] = hero_data
    data['hero']['diary'] = heroes_tt_api.diary_version(account.id)

    data['is_old'] = (data['hero']['actual_on_turn'] < turn_number)

    if is_own:
        data['energy'] = tt_api.energy_balance(account.id)
    else:
        data['energy'] = None

    return data


def form_game_info(account=None, is_own=False, client_turns=None):
    from the_tale.accounts.prototypes import AccountPrototype
    from the_tale.game.prototypes import GameState
    from the_tale.game.pvp.prototypes import Battle1x1Prototype

    data = {'mode': 'pve',
            'turn': turn.ui_info(),
            'game_state': GameState.state().value,
            'map_version': map_info_storage.version,
            'account': None,
            'enemy': None}

    if account:
        turn_number = turn.number()

        battle = Battle1x1Prototype.get_by_account_id(account.id)
        data['account'] = _form_game_account_info(turn_number,
                                                  account,
                                                  in_pvp_queue=False if battle is None else battle.state.is_WAITING,
                                                  is_own=is_own,
                                                  client_turns=client_turns)

        if battle and battle.state.is_PROCESSING:
            data['mode'] = 'pvp'
            data['enemy'] = _form_game_account_info(turn_number,
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


def game_diary_url():
    arguments = {'api_version': conf.game_settings.DIARY_API_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:api-diary', **arguments)


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


def _game_info_from_1_5_to_1_4__heroes(data):
    if 'quests' not in data:
        return

    if 'quests' not in data['quests']:
        return

    for quest in data['quests']['quests']:
        for quest_info in quest['line']:
            for name, type, actor_data in quest_info['actors']:
                if type == 0:
                    actor_data['mastery'] = 1
                    actor_data['mastery_verbose'] = 'гений'


def _game_info_from_1_6_to_1_5__heroes(data):
    data['pvp'] = {'advantage': 0,
                   'effectiveness': 0,
                   'probabilities': {'ice': 0,
                                     'blood': 0,
                                     'flame': 0 },
                    'energy': 0,
                    'energy_speed': 0}
    data['diary'] = []


def _game_info_from_1_8_to_1_7__heroes(data):
    if 'cards' in data['cards']:
        data['cards']['cards'] = []


def _game_info_from_1_9_to_1_8__heroes(data):
    data['energy'] = {'bonus': 0,
                      'max': 0,
                      'value': 0,
                      'discount': 0}

    data['cards'] = {'help_count': 0,
                     'help_barrier': 0}


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


def game_info_from_1_5_to_1_4(data):
    if data['account'] is not None:
        _game_info_from_1_5_to_1_4__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_5_to_1_4__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_6_to_1_5(data):
    if data['account'] is not None:
        _game_info_from_1_6_to_1_5__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_6_to_1_5__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_7_to_1_6(data):
    if data['account'] is not None:
        data['account']['new_messages'] = 0

    if data['enemy'] is not None:
        data['enemy']['new_messages'] = 0

    return data


def game_info_from_1_8_to_1_7(data):
    if data['account'] is not None:
        _game_info_from_1_8_to_1_7__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_8_to_1_7__heroes(data['enemy']['hero'])

    return data


def game_info_from_1_9_to_1_8(data):
    if data['account'] is not None:
        _game_info_from_1_9_to_1_8__heroes(data['account']['hero'])

    if data['enemy'] is not None:
        _game_info_from_1_9_to_1_8__heroes(data['enemy']['hero'])

    return data


def accounts_info(accounts_ids):
    from the_tale.accounts import prototypes as accounts_prototypes

    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}
    heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(list(accounts_ids))}

    accounts_data = {}

    for account in accounts.values():
        hero = heroes[account.id]

        hero_data = {'id': hero.id,
                     'name': hero.name,
                     'race': hero.race.value,
                     'gender': hero.gender.value,
                     'level': hero.level}

        account_data = {'id': account.id,
                        'name': account.nick_verbose,
                        'hero': hero_data,
                        'clan': account.clan_id}

        accounts_data[account.id] = account_data

    return accounts_data


def clans_info(accounts_data):
    from the_tale.accounts.clans import prototypes as clans_prototypes

    clans_ids = set(account['clan'] for account in accounts_data.values() if account['clan'] is not None)
    return {clan.id: {'id': clan.id,
                      'abbr': clan.abbr,
                      'name': clan.name}
            for clan in clans_prototypes.ClanPrototype.get_list_by_id(list(clans_ids))}
