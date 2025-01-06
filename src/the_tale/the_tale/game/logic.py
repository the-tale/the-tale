
import smart_imports

smart_imports.all()


@places_storage.places.postpone_version_update
@places_storage.buildings.postpone_version_update
@persons_storage.persons.postpone_version_update
@roads_storage.roads.postpone_version_update
@mobs_storage.mobs.postpone_version_update
@artifacts_storage.artifacts.postpone_version_update
def create_test_map():
    linguistics_logic.sync_static_restrictions()

    politic_power_storage.places.reset()
    politic_power_storage.persons.reset()

    tt_services.debug_clear_service()

    map_logic.create_test_map_info()

    p1 = places_logic.create_place(x=1, y=1, size=1, utg_name=game_names.generator().get_test_name(name='1x1'), race=relations.RACE.HUMAN)
    p2 = places_logic.create_place(x=3, y=3, size=3, utg_name=game_names.generator().get_test_name(name='10x10'), race=relations.RACE.HUMAN)
    p3 = places_logic.create_place(x=1, y=3, size=3, utg_name=game_names.generator().get_test_name(name='1x10'), race=relations.RACE.HUMAN)

    for place in places_storage.places.all():
        for i in range(3):
            persons_logic.create_person(place=place,
                                        race=relations.RACE.random(),
                                        gender=relations.GENDER.random(),
                                        type=persons_relations.PERSON_TYPE.random(),
                                        utg_name=game_names.generator().get_test_name())

    roads_logic.create_road(place_1=p1, place_2=p2, path='rdrd')
    roads_logic.create_road(place_1=p2, place_2=p3, path='ll')

    map_storage.cells.sync(force=True)

    for place in places_storage.places.all():
        place.refresh_attributes()

    places_storage.places.save_all()
    persons_storage.persons.save_all()

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


def remove_game_data(account):
    heroes_logic.remove_hero(account_id=account.id)


def _form_game_account_info(turn_number, account, is_own, client_turns=None):
    data = {'id': account.id,
            'last_visit': time.mktime((account.active_end_at - datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT)).timetuple()),
            'is_own': is_own,
            'is_old': False,
            'hero': None}

    hero_data = heroes_objects.Hero.cached_ui_info_for_hero(account_id=account.id,
                                                            recache_if_required=is_own,
                                                            patch_turns=client_turns,
                                                            for_last_turn=(not is_own))

    data['hero'] = hero_data

    # code is changed due to moving game to read-only mode
    data['hero']['diary'] = []

    # For game in the readonly we treate all heroes as actualp
    data['is_old'] = False  # (data['hero']['actual_on_turn'] < turn_number)

    return data


def form_game_info(account=None, is_own=False, client_turns=None):
    data = {'mode': 'pve',
            'turn': game_turn.ui_info(),
            'game_state': prototypes.GameState.state().value,
            'map_version': map_storage.map_info.version,
            'account': None,
            'enemy': None}

    if account:
        turn_number = game_turn.number()

        data['account'] = _form_game_account_info(turn_number,
                                                  account,
                                                  is_own=is_own,
                                                  client_turns=client_turns)

        action_data = data['account']['hero']['action'].get('data')

        if action_data and action_data.get('is_pvp'):
            data['mode'] = 'pvp'
            data['enemy'] = _form_game_account_info(turn_number,
                                                    accounts_prototypes.AccountPrototype.get_by_id(action_data['enemy_id']),
                                                    is_own=False,
                                                    client_turns=client_turns)

    return data


def game_info_url(account_id=None, client_turns=None):
    arguments = {'api_version': conf.settings.INFO_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    if account_id is not None:
        arguments['account'] = account_id

    if client_turns:
        arguments['client_turns'] = ','.join(str(turn) for turn in client_turns)

    return utils_urls.url('game:api-info', **arguments)


def game_diary_url():
    arguments = {'api_version': conf.settings.DIARY_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:api-diary', **arguments)


def game_names_url():
    arguments = {'api_version': conf.settings.NAMES_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:api-names', **arguments)


def game_hero_history_url():
    arguments = {'api_version': conf.settings.HERO_HISTORY_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:api-hero-history', **arguments)


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
                                     'flame': 0},
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


def game_info_from_1_10_to_1_9(data):
    if data['account'] is not None:
        data['account']['energy'] = 0

    if data['enemy'] is not None:
        data['enemy']['energy'] = None

    return data


def accounts_info(accounts_ids):
    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}
    heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(list(accounts_ids))}

    accounts_data = {}

    for account in accounts.values():
        hero = heroes[account.id]

        hero_data = {'id': hero.id,
                     'name': hero.name,
                     'race': hero.race.value,
                     'gender': hero.gender.value,
                     'level': hero.level,
                     'power': hero.power.ui_info()}

        account_data = {'id': account.id,
                        'name': account.nick_verbose,
                        'hero': hero_data,
                        'clan': account.clan_id}

        accounts_data[account.id] = account_data

    return accounts_data


def clans_info(accounts_data):
    clans_ids = set(account['clan'] for account in accounts_data.values() if account['clan'] is not None)
    return {clan.id: {'id': clan.id,
                      'abbr': clan.abbr,
                      'name': clan.name}
            for clan in clans_logic.load_clans(list(clans_ids))}


def hero_name_from_forms(name_forms, gender):
    return lexicon_dictionary.noun(name_forms + [''] * 6,
                                   'мр,од,ед' if gender.is_MALE else 'жр,од,ед')


def generate_history(name_forms, gender, race, honor, peacefulness, archetype, upbringing, first_death, age):
    name = hero_name_from_forms(name_forms, gender)

    restrictions = (linguistics_restrictions.get(gender),
                    linguistics_restrictions.get(race),
                    linguistics_restrictions.get(honor),
                    linguistics_restrictions.get(peacefulness),
                    linguistics_restrictions.get(archetype),
                    linguistics_restrictions.get(upbringing),
                    linguistics_restrictions.get(first_death),
                    linguistics_restrictions.get(age))

    hero_variable = linguistics_objects.UTGVariable(word=name, restrictions=restrictions)

    types = ['hero_history_birth',
             'hero_history_childhood',
             'hero_history_death']

    texts = []

    for type in types:
        lexicon_key, externals, restrictions = linguistics_logic.prepair_get_text(type, {'hero': hero_variable})

        text = linguistics_logic.render_text(lexicon_key=lexicon_key,
                                             externals=externals,
                                             restrictions=restrictions,
                                             quiet=True,
                                             with_nearest_distance=True,
                                             fake_text=lambda *argv, **kwargs: None)
        texts.append(text)

    return texts


@places_storage.places.postpone_version_update
@places_storage.buildings.postpone_version_update
@persons_storage.persons.postpone_version_update
def highlevel_step(logger):

    logger.info('sync data')

    call_after_transaction = []

    with django_transaction.atomic():
        logger.info('sync data transaction started')

        try:
            politic_power_logic.sync_power()
            places_logic.sync_fame()
            places_logic.sync_money()
        except tt_api_exceptions.TTAPIError as e:
            sentry_sdk.capture_exception(e)
            logger.exception('Error while syncing powers')

        # обрабатывает работы только во время запланированного обновления
        # поскольку при остановке игры нельзя будет обработать команды для героев
        # (те уже будут сохраняться в базу, рабочие логики будут недоступны)
        for person in persons_storage.persons.all():
            call_after_transaction.extend(jobs_logic.update_job(person.job, person.id))

        frontier_places = [place for place in places_storage.places.all() if place.is_frontier]
        core_places = [place for place in places_storage.places.all() if not place.is_frontier]

        places_logic.sync_power_economic(frontier_places,
                                         max_economic=c.PLACE_MAX_FRONTIER_ECONOMIC)
        places_logic.sync_power_economic(core_places,
                                         max_economic=c.PLACE_MAX_ECONOMIC)

        places_logic.sync_money_economic(frontier_places,
                                         max_economic=c.PLACE_MAX_FRONTIER_ECONOMIC)
        places_logic.sync_money_economic(core_places,
                                         max_economic=c.PLACE_MAX_ECONOMIC)

        places_logic.update_effects()

        areas = map_storage.cells.get_places_areas()

        for place in places_storage.places.all():
            place.attrs.sync_size(c.MAP_SYNC_TIME_HOURS)
            place.attrs.set_area(areas[place.id])

            place.sync_race()
            place.sync_habits()
            place.update_heroes_habits()

            # must be last operation to display and use real data
            place.refresh_attributes()

            place.mark_as_updated()

        places_storage.places.save_all()
        persons_storage.persons.save_all()

    logger.info('sync data transaction completed')

    logger.info('after transaction operations number: {number}'.format(number=len(call_after_transaction)))

    for operation in call_after_transaction:
        operation()

    logger.info('sync data completed')
