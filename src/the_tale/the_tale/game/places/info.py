
import smart_imports

smart_imports.all()


def place_info_persons_data(place, full_building_info):
    data = []

    for person in place.persons:
        building = storage.buildings.get_by_person_id(person.id)

        person_data = {'id': person.id,
                       'name': person.name,
                       'gender': person.gender.value,
                       'race': person.race.value,
                       'type': person.type.value,
                       'building': None,
                       'next_move_available_in': person.seconds_before_next_move,
                       'politic_power_fraction': politic_power_storage.persons.total_power_fraction(person.id),
                       'personality': {'cosmetic': person.personality_cosmetic.value,
                                       'practical': person.personality_practical.value}}

        if building:
            person_data['building'] = building_info(building) if full_building_info else building.id

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
            properties.append('%s за %s' % (resource_1.text, resource_2.text))
        else:
            if not resource_1.is_NONE:
                properties.append('%s получает %s' % (place_2.name, resource_1.text))
            if not resource_2.is_NONE:
                properties.append('%s отправляет %s' % (place_2.name, resource_2.text))

        data.append({'id': exchange.bill.id,
                     'caption': exchange.bill.caption,
                     'properties': properties})

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
                                                           'negative_points': place.habit_peacefulness_negative}}


def place_info(place, full_building_info):

    inner_circle = politic_power_logic.get_inner_circle(place_id=place.id)

    data = {'id': place.id,
            'name': place.name,
            'frontier': place.is_frontier,
            'new_for': time.mktime(place.new_for.timetuple()),
            'description': place.description_html,
            'updated_at': time.mktime(place.updated_at.timetuple()),
            'position': {'x': place.x, 'y': place.y},
            'politic_power': {'heroes': inner_circle.ui_info(),
                              'power': politic_power_storage.places.ui_info(place.id)},
            'persons': place_info_persons_data(place, full_building_info=full_building_info),
            'attributes': game_attributes.attributes_info(effects=place.all_effects(),
                                                          attrs=place.attrs,
                                                          relation=relations.ATTRIBUTE),
            'demographics': place_info_demographics(place),
            'bills': place_info_bills(place),
            'habits': place_info_habits(place),
            'job': place.job.ui_info(),
            'chronicle': chronicle_prototypes.chronicle_info(place, conf.settings.CHRONICLE_RECORDS_NUMBER),
            'accounts': None,
            'clans': None}

    accounts_ids = set()
    accounts_ids.update(data['politic_power']['heroes']['positive'])
    accounts_ids.update(data['politic_power']['heroes']['negative'])

    data['accounts'] = game_logic.accounts_info(accounts_ids)
    data['clans'] = game_logic.clans_info(data['accounts'])

    return data


def building_info(building):
    return {'id': building.id,
            'position': {'x': building.x, 'y': building.y},
            'type': building.type.value,
            'integrity': building.integrity,
            'created_at_turn': building.created_at_turn}
