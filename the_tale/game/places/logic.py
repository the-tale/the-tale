# coding: utf-8
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from utg import words as utg_words

from the_tale.game.balance import formulas as f

from the_tale.game.prototypes import TimePrototype
from the_tale.game import relations as game_relations
from the_tale.game import names

from the_tale.game.jobs import job
from the_tale.game import politic_power
from the_tale.game import effects

from . import races
from . import conf
from . import models
from . import objects
from . import habits
from . import attributes
from . import modifiers
from . import signals
from . import relations


EffectsContainer = effects.create_container(relations.ATTRIBUTE)


class PlaceJob(job.Job):
    ACTOR = 'place'


class PlacePoliticPower(politic_power.PoliticPower):
    INNER_CIRCLE_SIZE = 7

    def change_power(self, place, hero_id, has_in_preferences, power):
        power *= place.attrs.freedom
        super(PlacePoliticPower, self).change_power(owner=place, hero_id=hero_id, has_in_preferences=has_in_preferences, power=power)

    def job_effect_kwargs(self, place):
        return {'actor_type': 'place',
                'actor_name': place.name,
                'person': None,
                'place': place,
                'positive_heroes': self.inner_positive_heroes,
                'negative_heroes': self.inner_negative_heroes,
                'job_power': place.get_job_power() }


# умножаем на 2, так как кажая остановка в городе, по сути, даёт влияние в 2-кратном размере
# Город получит влияние и от задания, которое герой выполнил и от того, которое возьмёт
NORMAL_PLACE_JOB_POWER = f.normal_job_power(PlacePoliticPower.INNER_CIRCLE_SIZE) * 2


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

    place = objects.Place(id=place_model.id,
                          x=place_model.x,
                          y=place_model.y,
                          created_at_turn=place_model.created_at_turn,
                          updated_at_turn=place_model.updated_at_turn,
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
                          politic_power=PlacePoliticPower.deserialize(data['politic_power']) if 'politic_power'in data else PlacePoliticPower.create(),
                          utg_name=utg_words.Word.deserialize(data['name']),
                          attrs=attributes.Attributes.deserialize(data.get('attributes', {})),
                          races=races.Races.deserialize(data['races']),
                          nearest_cells=data.get('nearest_cells', []),
                          effects=EffectsContainer.deserialize(data.get('effects')),
                          job=PlaceJob.deserialize(data['job']) if 'job' in data else PlaceJob.create(normal_power=NORMAL_PLACE_JOB_POWER),
                          modifier=place_model.modifier)

    place.attrs.sync()

    return place

def save_place(place, new=False):
    from the_tale.game.places import storage

    data = {'name': place.utg_name.serialize(),
            'attributes': place.attrs.serialize(),
            'races': place.races.serialize(),
            'nearest_cells': place.nearest_cells,
            'effects': place.effects.serialize(),
            'job': place.job.serialize(),
            'politic_power': place.politic_power.serialize()}

    arguments = { 'x': place.x,
                  'y': place.y,
                  'updated_at_turn': TimePrototype.get_current_turn_number(),
                  'updated_at': datetime.datetime.now(),
                  'is_frontier': place.is_frontier,
                  'description': place.description,
                  'data': s11n.to_json(data),
                  'habit_honor_positive': place.habit_honor_positive,
                  'habit_honor_negative': place.habit_honor_negative,
                  'habit_peacefulness_positive': place.habit_peacefulness_positive,
                  'habit_peacefulness_negative': place.habit_peacefulness_negative,
                  'habit_honor': place.habit_honor.raw_value,
                  'habit_peacefulness': place.habit_peacefulness.raw_value,
                  'modifier': place._modifier,
                  'race': place.race,
                  'persons_changed_at_turn': place.persons_changed_at_turn}

    if new:
        place_model = models.Place.objects.create(created_at_turn=TimePrototype.get_current_turn_number(), **arguments)
        place.id = place_model.id
        storage.places.add_item(place.id, place)
    else:
        models.Place.objects.filter(id=place.id).update(**arguments)

    storage.places.update_version()

    place.updated_at = datetime.datetime.now()



def create_place(x, y, size, utg_name, race, is_frontier=False):
    place = objects.Place(id=None,
                          x=x,
                          y=y,
                          updated_at=datetime.datetime.now(),
                          updated_at_turn=TimePrototype.get_current_turn_number(),
                          created_at=datetime.datetime.now(),
                          created_at_turn=TimePrototype.get_current_turn_number(),
                          habit_honor=habits.Honor(raw_value=0),
                          habit_honor_positive=0,
                          habit_honor_negative=0,
                          habit_peacefulness=habits.Peacefulness(raw_value=0),
                          habit_peacefulness_positive=0,
                          habit_peacefulness_negative=0,
                          is_frontier=is_frontier,
                          description=u'',
                          race=race,
                          persons_changed_at_turn=TimePrototype.get_current_turn_number(),
                          politic_power=PlacePoliticPower.create(),
                          attrs=attributes.Attributes(size=size),
                          utg_name=utg_name,
                          races=races.Races(),
                          nearest_cells=[],
                          effects=EffectsContainer(),
                          job=PlaceJob.create(normal_power=NORMAL_PLACE_JOB_POWER),
                          modifier=modifiers.CITY_MODIFIERS.NONE)
    place.refresh_attributes()
    save_place(place, new=True)
    return place


def add_person_to_place(place):
    from the_tale.game.persons import relations as persons_relations
    from the_tale.game.persons import logic as persons_logic

    race = game_relations.RACE.random()

    gender = game_relations.GENDER.random(exclude=(game_relations.GENDER.NEUTER,))

    new_person = persons_logic.create_person(place=place,
                                             race=race,
                                             gender=gender,
                                             type=persons_relations.PERSON_TYPE.random(),
                                             utg_name=names.generator.get_name(race, gender))

    signals.place_person_arrived.send(place.__class__, place=place, person=new_person)

    place.refresh_attributes()

    return new_person



def api_list_url():
    arguments = {'api_version': conf.settings.API_LIST_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:places:api-list', **arguments)


def api_show_url(place):
    arguments = {'api_version': conf.settings.API_SHOW_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:places:api-show', place.id, **arguments)


def refresh_all_places_attributes():
    from the_tale.game.places import storage

    for place in storage.places.all():
        place.refresh_attributes()
        save_place(place)
