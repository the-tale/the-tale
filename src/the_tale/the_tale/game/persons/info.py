
import smart_imports

smart_imports.all()


def person_info(person):
    building = places_storage.buildings.get_by_person_id(person.id)

    inner_circle = politic_power_logic.get_inner_circle(person_id=person.id)

    total_events, events = chronicle_tt_services.chronicle.cmd_get_last_events(tags=[person.meta_object().tag],
                                                                               number=conf.settings.CHRONICLE_RECORDS_NUMBER)

    tt_api_events_log.fill_events_wtih_meta_objects(events)

    data = {'id': person.id,
            'name': person.name,
            'updated_at': time.mktime(person.updated_at.timetuple()),

            'profession': person.type.value,
            'race': person.race.value,
            'gender': person.gender.value,

            'place': {
                'id': person.place.id,
                'name': person.place.name,
                'size': person.place.attrs.size,
                'specialization': person.place.modifier.value,
                'position': {'x': person.place.x, 'y': person.place.y}
            },

            'building': places_info.building_info(building) if building else None,
            'politic_power': {'heroes': inner_circle.ui_info(),
                              'power': politic_power_storage.persons.ui_info(person.id)},
            'attributes': game_attributes.attributes_info(effects=person.all_effects(),
                                                          attrs=person.attrs,
                                                          relation=relations.ATTRIBUTE),
            'chronicle': [event.ui_info() for event in events],
            'job': person.job.ui_info(person.id),
            'accounts': None,
            'clans': None}

    accounts_ids = set()
    accounts_ids.update(hero_id for hero_id, power in data['politic_power']['heroes']['rating'])

    data['accounts'] = game_logic.accounts_info(accounts_ids)
    data['clans'] = game_logic.clans_info(data['accounts'])

    return data
