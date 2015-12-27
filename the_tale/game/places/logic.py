# coding: utf-8
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from utg import words as utg_words

from the_tale.game.prototypes import TimePrototype

from . import races
from . import conf
from . import models
from . import objects
from . import habits
from . import attributes
from . import effects


def load_place(place_id=None, place_model=None):

    # TODO: get values instead model
    # TODO: check that load_hero everywhere called with correct arguments
    try:
        if place_id is not None:
            place_model = models.Place.objects.get(id=place_id)
        elif place_model is None:
            return None
    except models.Place.DoesNotExist:
        return None

    data = s11n.from_json(place_model.data)

    if 'nearest_cells' in data:
        data['nearest_cells'] = map(tuple, data['nearest_cells'])

    return objects.Place(id=place_model.id,
                         x=place_model.x,
                         y=place_model.y,
                         heroes_number=place_model.heroes_number,
                         updated_at=place_model.updated_at,
                         created_at=place_model.created_at,
                         habit_honor=habits.Honor(raw_value=place_model.habit_honor),
                         habit_honor_positive=place_model.habit_honor_positive,
                         habit_honor_negative=place_model.habit_honor_negative,
                         habit_peacefulness=habits.Peacefulness(raw_value=place_model.habit_peacefulness),
                         habit_peacefulness_positive=place_model.habit_peacefulness_positive,
                         habit_peacefulness_negative=place_model.habit_peacefulness_negative,
                         is_frontier=place_model.is_frontier,
                         description=place_model.description,
                         race=place_model.race,
                         persons_changed_at_turn=place_model.persons_changed_at_turn,
                         power=place_model.power,
                         utg_name=utg_words.Word.deserialize(data['name']),
                         attrs=attributes.Attributes.deserialize(data['attributes']),
                         races=races.Races.deserialize(data['races']),
                         nearest_cells=data.get('nearest_cells', []),
                         effects=effects.Container.deserialize(data.get('effects')))


def save_place(place, new=False):
    from the_tale.game.places import storage

    data = {'name': place.utg_name.serialize(),
            'attributes': place.attrs.serialize(),
            'races': place.races.serialize(),
            'nearest_cells': place.nearest_cells,
            'effects': place.effects.serialize()}

    arguments = { 'x': place.x,
                  'y': place.y,
                  'updated_at_turn': TimePrototype.get_current_turn_number(),
                  'updated_at': datetime.datetime.now(),
                  'is_frontier': place.is_frontier,
                  'description': place.description,
                  'data': data,
                  'heroes_number': place.heroes_number,
                  'habit_honor_positive': place.habit_honor_positive,
                  'habit_honor_negative': place.habit_honor_negative,
                  'habit_peacefulness_positive': place.habit_peacefulness_positive,
                  'habit_peacefulness_negative': place.habit_peacefulness_negative,
                  'habit_honor': place.habit_honor.raw_value,
                  'habit_peacefulness': place.habit_peacefulness.raw_value,
                  'modifier': place.modifier,
                  'race': place.race,
                  'persons_changed_at_turn': place.persons_changed_at_turn,
                  'power': place.power}

    if new:
        place_model = models.Place.objects.create(**arguments)
        place.id = place_model.id

        storage.places.add_item(place.id, place)
        storage.places.update_version()
    else:
        place_model = models.Place.objects.filter(id=place.id,
                                                  created_at_turn=TimePrototype.get_current_turn_number()).update(**arguments)

    place.updated_at = place_model.updated_at


def api_list_url():
    arguments = {'api_version': conf.places_settings.API_LIST_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:map:places:api-list', **arguments)


def api_show_url(place):
    arguments = {'api_version': conf.places_settings.API_SHOW_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:map:places:api-show', place.id, **arguments)
