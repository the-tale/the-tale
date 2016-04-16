# coding: utf-8

import time

from the_tale.game import relations as game_relations

from the_tale.game.chronicle import prototypes as chronicle_prototypes

from the_tale.game import attributes
from the_tale.game import logic as game_logic

from . import storage
from . import relations
from . import conf


def place_info_persons_data(place):
    data = []

    for person in place.persons:
        building = storage.buildings.get_by_person_id(person.id)

        person_data = {'id': person.id,
                       'name': person.name,
                       'gender': person.gender.value,
                       'race': person.race.value,
                       'type': person.type.value,
                       'next_move_available_in': person.seconds_before_next_move,
                       'politic_power_fraction': person.total_politic_power_fraction,
                       'building': building.id if building else None,
                       'personality': { 'cosmetic': person.personality_cosmetic.value,
                                        'practical': person.personality_practical.value } }
        data.append(person_data)

    return data


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



def place_info(place):
    data = {'id': place.id,
            'name': place.name,
            'frontier': place.is_frontier,
            'new_for': time.mktime(place.new_for.timetuple()),
            'description': place.description_html,
            'updated_at': time.mktime(place.updated_at.timetuple()),
            'position': {'x': place.x, 'y': place.y},
            'politic_power': place.politic_power.ui_info([p.politic_power for p in place.get_same_places()]),
            'persons': place_info_persons_data(place),
            'attributes': attributes.attributes_info(effects=place.all_effects(),
                                                     attrs=place.attrs,
                                                     relation=relations.ATTRIBUTE),
            'demographics': place_info_demographics(place),
            'bills': place_info_bills(place),
            'habits': place_info_habits(place),
            'chronicle': chronicle_prototypes.chronicle_info(place, conf.settings.CHRONICLE_RECORDS_NUMBER),
            'accounts': None,
            'clans': None
           }

    accounts_ids = set()
    accounts_ids.update(data['politic_power']['heroes']['positive'])
    accounts_ids.update(data['politic_power']['heroes']['negative'])

    data['accounts'] = game_logic.accounts_info(accounts_ids)
    data['clans'] = game_logic.clans_info(data['accounts'])

    return data
