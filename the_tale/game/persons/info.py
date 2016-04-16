# coding: utf-8

import time

from the_tale.game.chronicle import prototypes as chronicle_prototypes

from the_tale.game import attributes
from the_tale.game import logic as game_logic

from . import conf
from . import relations


def person_info(person):

    data = {'id': person.id,
            'name': person.name,
            'updated_at': time.mktime(person.updated_at.timetuple()),

            'place': {
                'id': person.place.id,
                'name': person.place.name,
                'size': person.place.attrs.size,
                'specialization': person.place.modifier.value,
                'position': {'x': person.place.x, 'y': person.place.y}
            },

            'politic_power': person.politic_power.ui_info([p.politic_power for p in person.place.persons]),
            'attributes': attributes.attributes_info(effects=person.all_effects(),
                                                     attrs=person.attrs,
                                                     relation=relations.ATTRIBUTE),
            'chronicle': chronicle_prototypes.chronicle_info(person, conf.settings.CHRONICLE_RECORDS_NUMBER),
            'accounts': None,
            'clans': None
           }

    accounts_ids = set()
    accounts_ids.update(data['politic_power']['heroes']['positive'])
    accounts_ids.update(data['politic_power']['heroes']['negative'])

    data['accounts'] = game_logic.accounts_info(accounts_ids)
    data['clans'] = game_logic.clans_info(data['accounts'])

    return data
