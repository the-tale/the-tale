# coding: utf-8
import random
import datetime
from django.conf import settings as project_settings

from utg import words as utg_words

from dext.common.utils import s11n
from dext.common.utils.urls import url

from the_tale.game import prototypes as game_protypes

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.prototypes import TimePrototype

from the_tale.game.roads.storage import waymarks_storage

from the_tale.game.jobs import job
from the_tale.game import politic_power

from . import models
from . import objects
from . import storage
from . import conf
from . import relations
from . import exceptions
from . import attributes


class PersonJob(job.Job):
    ACTOR = 'person'


class PersonPoliticPower(politic_power.PoliticPower):
    INNER_CIRCLE_SIZE = 3

    def change_power(self, person, hero_id, has_in_preferences, power):
        power_multiplier = 1

        if person.has_building:
            power_multiplier += c.BUILDING_PERSON_POWER_BONUS

        # this power will go to person and to place
        place_power = power * power_multiplier

        # this power, only to person
        person_power = power * power_multiplier * person.place.attrs.freedom

        super(PersonPoliticPower, self).change_power(owner=person, hero_id=hero_id, has_in_preferences=has_in_preferences, power=person_power)

        return place_power

    def job_effect_kwargs(self, person):
        return {'actor_type': 'person',
                'actor_name': person.name,
                'person': person,
                'place': person.place,
                'positive_heroes': self.inner_positive_heroes,
                'negative_heroes': self.inner_negative_heroes,
                'job_power': person.get_job_power() }


NORMAL_PERSON_JOB_POWER = f.normal_job_power(PersonPoliticPower.INNER_CIRCLE_SIZE)


def save_person(person, new=False):

    data = {'name': person.utg_name.serialize(),
            'job': person.job.serialize(),
            'politic_power': person.politic_power.serialize(),
            'moved_at_turn': person.moved_at_turn,
            'attributes': person.attrs.serialize(),
            'personality': {'cosmetic': person.personality_cosmetic.value,
                            'practical': person.personality_practical.value}}

    arguments = {'place_id': person.place_id,
                 'gender': person.gender,
                 'race': person.race,
                 'type': person.type,
                 'data': s11n.to_json(data),
                 'created_at_turn': person.created_at_turn,
                 'updated_at_turn': person.updated_at_turn}

    if new:
        person_model = models.Person.objects.create(**arguments)

        person.id = person_model.id

        # TODO: that string was in .create method, is it needed here?
        person.place.persons_changed_at_turn = game_protypes.TimePrototype.get_current_turn_number()

        storage.persons.add_item(person.id, person)
    else:
        models.Person.objects.filter(id=person.id).update(**arguments)

    storage.persons.update_version()


def create_person(place, race, type, utg_name, gender, personality_cosmetic=None, personality_practical=None):

    if personality_cosmetic is None:
        personality_cosmetic = relations.PERSONALITY_COSMETIC.random()

    if personality_practical is None:
        personality_practical = relations.PERSONALITY_PRACTICAL.random()

    person = objects.Person(id=None,
                            created_at_turn=TimePrototype.get_current_turn_number(),
                            updated_at_turn=TimePrototype.get_current_turn_number(),
                            updated_at=datetime.datetime.now(),
                            place_id=place.id,
                            gender=gender,
                            race=race,
                            type=type,
                            attrs=attributes.Attributes(),
                            personality_cosmetic=personality_cosmetic,
                            personality_practical=personality_practical,
                            politic_power=PersonPoliticPower.create(),
                            utg_name=utg_name,
                            job=PersonJob.create(normal_power=NORMAL_PERSON_JOB_POWER),
                            moved_at_turn=TimePrototype.get_current_turn_number())
    person.refresh_attributes()
    place.refresh_attributes()
    save_person(person, new=True)
    return person


def load_person(person_id=None, person_model=None):
    # TODO: get values instead model
    # TODO: check that load_hero everywhere called with correct arguments
    try:
        if person_id is not None:
            person_model = models.Person.objects.get(id=person_id)
        elif person_model is None:
            return None
    except models.Person.DoesNotExist:
        return None

    data = s11n.from_json(person_model.data)

    return objects.Person(id=person_model.id,
                          created_at_turn=person_model.created_at_turn,
                          updated_at_turn=person_model.updated_at_turn,
                          place_id=person_model.place_id,
                          gender=person_model.gender,
                          race=person_model.race,
                          type=person_model.type,
                          attrs=attributes.Attributes.deserialize(data.get('attributes', {})),
                          politic_power=PersonPoliticPower.deserialize(data['politic_power']) if 'politic_power'in data else PersonPoliticPower.create(),
                          utg_name=utg_words.Word.deserialize(data['name']),
                          job=PersonJob.deserialize(data['job']) if 'job' in data else PersonJob.create(normal_power=NORMAL_PERSON_JOB_POWER),
                          personality_cosmetic=relations.PERSONALITY_COSMETIC(data['personality']['cosmetic']),
                          personality_practical=relations.PERSONALITY_PRACTICAL(data['personality']['practical']),
                          moved_at_turn=data.get('moved_at_turn', 0),
                          updated_at=person_model.updated_at)


def social_connection_from_model(model):
    return objects.SocialConnection(id=model.id,
                                    connection=model.connection,
                                    person_1_id=model.person_1_id,
                                    person_2_id=model.person_2_id,
                                    created_at=model.created_at,
                                    created_at_turn=model.created_at_turn,
                                    state=model.state)


def create_social_connection(connection_type, person_1, person_2):

    if person_1.id > person_2.id:
        person_1, person_2 = person_2, person_1

    if person_1.place_id == person_2.place_id:
        raise exceptions.PersonsFromOnePlaceError(person_1_id=person_1.id, person_2_id=person_2.id)

    if storage.social_connections.is_connected(person_1, person_2):
        raise exceptions.PersonsAlreadyConnectedError(person_1_id=person_1.id, person_2_id=person_2.id)

    model = models.SocialConnection.objects.create(created_at_turn=game_protypes.TimePrototype.get_current_turn_number(),
                                                   person_1_id=person_1.id,
                                                   person_2_id=person_2.id,
                                                   connection=connection_type,
                                                   state=relations.SOCIAL_CONNECTION_STATE.IN_GAME)

    connection = social_connection_from_model(model)

    storage.social_connections.add_item(connection.id, connection)
    storage.social_connections.update_version()

    return connection


# TODO: this method may cause large db usage on removing multiple connections
def remove_connection(connection):
    models.SocialConnection.objects.filter(id=connection.id).update(state=relations.SOCIAL_CONNECTION_STATE.OUT_GAME,
                                                                    out_game_at=datetime.datetime.now(),
                                                                    out_game_at_turn=game_protypes.TimePrototype.get_current_turn_number())
    storage.social_connections.update_version()
    storage.social_connections.refresh()



def get_next_connection_minimum_distance(person):
    if conf.settings.SOCIAL_CONNECTIONS_MINIMUM > len(storage.social_connections.get_connected_persons_ids(person)) + 1:
        return 0

    minimum_distance = conf.settings.SOCIAL_CONNECTIONS_MINIMUM * c.QUEST_AREA_RADIUS * conf.settings.SOCIAL_CONNECTIONS_AVERAGE_PATH_FRACTION

    for connected_person_id in storage.social_connections.get_connected_persons_ids(person):
        connected_person = storage.persons[connected_person_id]
        path_length = waymarks_storage.look_for_road(person.place, connected_person.place).length
        minimum_distance -= path_length

    return minimum_distance


def search_available_connections(person, minimum_distance=None):
    excluded_persons_ids = storage.social_connections.get_connected_persons_ids(person)

    persons = storage.persons.all()

    candidates = []

    if minimum_distance is None:
        minimum_distance = get_next_connection_minimum_distance(person)

    for candidate in persons:
        if candidate.id in excluded_persons_ids:
            continue

        if person.place_id == candidate.place_id:
            continue

        path_length = waymarks_storage.look_for_road(person.place, candidate.place).length

        if path_length > c.QUEST_AREA_RADIUS:
            continue

        if path_length < minimum_distance:
            continue

        candidates.append(candidate)

    if not candidates:
        return search_available_connections(person, minimum_distance * conf.settings.SOCIAL_CONNECTIONS_MIN_DISTANCE_DECREASE)

    return candidates


def create_missing_connection(person):

    candidates = search_available_connections(person)

    if not candidates:
        return None

    connected_person = random.choice(candidates)

    create_social_connection(connection_type=relations.SOCIAL_CONNECTION_TYPE.random(),
                             person_1=person,
                             person_2=connected_person)

    return connected_person


@storage.social_connections.postpone_version_update
def create_missing_connections():
    persons = storage.persons.all()

    for person in persons:
        connections = storage.social_connections.get_connected_persons_ids(person)
        while len(connections) < conf.settings.SOCIAL_CONNECTIONS_MINIMUM:
            connected_person = create_missing_connection(person)
            if connected_person is None:
                continue
            connections.append(connected_person.id)

def sync_social_connections():
    create_missing_connections()


def move_person_to_place(person, new_place):
    person.place_id = new_place.id
    person.moved_at_turn = TimePrototype.get_current_turn_number()

    save_person(person)


def api_show_url(person):
    arguments = {'api_version': conf.settings.API_SHOW_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('game:persons:api-show', person.id, **arguments)


def refresh_all_persons_attributes():
    for person in storage.persons.all():
        person.refresh_attributes()
        save_person(person)
