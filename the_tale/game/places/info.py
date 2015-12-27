# coding: utf-8

import time

from the_tale.game import relations as game_relations

from the_tale.game.chronicle import prototypes as chronicle_prototypes

from the_tale.accounts import prototypes as accounts_prototypes

from the_tale.game.heroes.preferences import HeroPreferences
from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.persons import storage as persons_storage

from . import storage


def place_info_persons_data(place):
    data = []

    for person in place.persons:
        building = storage.buildings.get_by_person_id(person.id)

        connections = [(connection_type.value, person_id)
                       for connection_type, person_id in persons_storage.social_connections.get_person_connections(person)]
        connections.sort()

        person_data = {'id': person.id,
                       'name': person.name,
                       'gender': person.gender.value,
                       'race': person.race.value,
                       'type': person.type.value,
                       'unfreeze_in': person.time_before_unfreeze.total_seconds(),
                       'mastery': {'value': person.mastery,
                                   'name': person.mastery_verbose},
                       'power': { 'percents': person.power / place.total_persons_power if place.total_persons_power > 0 else 0,
                                  'positive_bonus': person.power_positive,
                                  'negative_bonus': person.power_negative },
                       'building': building.id if building else None,
                       'connections': connections,
                       'keepers': {'friends': [hero.account_id for hero in HeroPreferences.get_friends_of(person, all=place.depends_from_all_heroes)],
                                   'enemies': [hero.account_id for hero in HeroPreferences.get_enemies_of(person, all=place.depends_from_all_heroes)]} }
        data.append(person_data)

    return data


def place_info_parameters(place):
    return {'size': {'value': place.size, 'modifiers': None},
            'economic': {'value': place.expected_size, 'modifiers': None},
            'politic_radius': {'value': place.terrain_owning_radius, 'modifiers': None},
            'terrain_radius': {'value': place.terrain_radius, 'modifiers': None},
            'stability': {'value': place.stability, 'modifiers': place.get_stability_powers()},
            'production': {'value': place.production, 'modifiers': place.get_production_powers()},
            'goods': {'value': place.goods, 'modifiers': None},
            'keepers_goods': {'value': place.keepers_goods, 'modifiers': None},
            'safety': {'value': place.safety, 'modifiers': place.get_safety_powers()},
            'transport': {'value': place.transport, 'modifiers': place.get_transport_powers()},
            'freedom': {'value': place.freedom, 'modifiers': place.get_freedom_powers()},
            'tax': {'value': place.tax, 'modifiers': place.get_tax_powers()} }


def place_info_demographics(place):
    data = []

    for race_info in place.races.demographics(place.persons):
        data.append({'race': race_info.race.value,
                     'percents': race_info.percents,
                     'delta': race_info.delta,
                     'persons': race_info.persons_percents})

    return data


def place_info_bills(place):
    data = []

    for exchange in storage.resource_exchanges.get_exchanges_for_place(place):
        resource_1, resource_2, place_2 = exchange.get_resources_for_place(place)
        properties = []

        if place_2 is None:
            properties.append(u'%s за %s' % (resource_1.text, resource_2.text))
        else:
            if not resource_1.is_NONE:
                properties.append(u'%s получает %s' % (place_2.name, resource_1.text))
            if not resource_2.is_NONE:
                properties.append(u'%s отправляет %s' % (place_2.name, resource_2.text))

        data.append({'id': exchange.bill.id,
                     'caption': exchange.bill.caption,
                     'properties':properties})

    return data


def place_info_specializations(place):
    data = {'current': place.modifier.TYPE.value if place.modifier else None,
            'all': []}

    for modifier in place.modifiers:
        data['all'].append({'value': modifier.TYPE.value,
                            'power': modifier.power,
                            'modifiers': modifier.power_effects_for_template,
                            'size_modifier': modifier.size_modifier})

    return data


def place_info_habits(place):
    return {game_relations.HABIT_TYPE.HONOR.value: {'interval': place.habit_honor.interval.value,
                                                    'value': place.habit_honor.raw_value,
                                                    'delta': place.habit_honor_change_speed,
                                                    'positive_points': place.habit_honor_positive,
                                                    'negative_points': place.habit_honor_negative},
            game_relations.HABIT_TYPE.PEACEFULNESS.value: {'interval': place.habit_peacefulness.interval.value,
                                                           'value': place.habit_peacefulness.raw_value,
                                                           'delta': place.habit_peacefulness_change_speed,
                                                           'positive_points': place.habit_peacefulness_positive,
                                                           'negative_points': place.habit_peacefulness_negative} }

def place_info_cronicle(place):
    return [(record.game_time.verbose_date_short, record.game_time.verbose_date, record.text)
            for record in chronicle_prototypes.RecordPrototype.get_last_actor_records(place, conf.places_settings.CHRONICLE_RECORDS_NUMBER)]


def place_info_accounts(data):
    accounts_ids = set()

    accounts_ids.update(data['keepers']['friends'])
    accounts_ids.update(data['keepers']['enemies'])

    for person in data['persons']:
        accounts_ids.update(person['keepers']['friends'])
        accounts_ids.update(person['keepers']['enemies'])

    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}
    heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(list(accounts_ids))}

    accounts_data = {}

    for account in accounts.itervalues():
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

def place_info_clans(data):
    from the_tale.accounts.clans import prototypes as clans_prototypes

    clans_ids = set(account['clan'] for account in data['accounts'].itervalues() if account['clan'] is not None)
    return {clan.id: {'id': clan.id,
                      'abbr': clan.abbr,
                      'name': clan.name}
            for clan in clans_prototypes.ClanPrototype.get_list_by_id(list(clans_ids))}

def place_info(place):
    data = {'id': place.id,
            'name': place.name,
            'frontier': place.is_frontier,
            'new_for': time.mktime(place.new_for.timetuple()),
            'position': {'x': place.x, 'y': place.y},

            'updated_at': time.mktime(place.updated_at.timetuple()),

            'power': { 'positive_bonus': place.power_positive,
                       'negative_bonus': place.power_negative },

            'description': place.description_html,

            'persons': place_info_persons_data(place),
            'keepers': {'friends': [hero.account_id for hero in HeroPreferences.get_citizens_of(place, all=place.depends_from_all_heroes)] ,
                        'enemies': []},
            'parameters': place_info_parameters(place),
            'demographics': place_info_demographics(place),
            'bills': place_info_bills(place),
            'specializations': place_info_specializations(place),
            'habits': place_info_habits(place),
            'chronicle': place_info_cronicle(place),
            'accounts': None,
            'clans': None
           }

    data['accounts'] = place_info_accounts(data)
    data['clans'] = place_info_clans(data)

    return data
