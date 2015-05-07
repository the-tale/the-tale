# coding: utf-8
import random
import datetime

from the_tale.game import prototypes as game_protypes

from the_tale.game.balance import constants as c

from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.persons import models
from the_tale.game.persons import objects
from the_tale.game.persons import storage
from the_tale.game.persons import conf
from the_tale.game.persons import relations
from the_tale.game.persons import exceptions


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
        connected_person = storage.persons_storage[connected_person_id]
        path_length = waymarks_storage.look_for_road(person.place, connected_person.place).length
        minimum_distance -= path_length

    return minimum_distance


def search_available_connections(person, minimum_distance=None):
    excluded_persons_ids = storage.social_connections.get_connected_persons_ids(person)

    persons = storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME)

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


def out_game_obsolete_connections():
    for connection in storage.social_connections.all():
        for person in connection.persons:
            if not person.state.is_IN_GAME:
                remove_connection(connection)


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
    persons = storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME)

    for person in persons:
        connections = storage.social_connections.get_connected_persons_ids(person)
        while len(connections) < conf.settings.SOCIAL_CONNECTIONS_MINIMUM:
            connected_person = create_missing_connection(person)
            if connected_person is None:
                continue
            connections.append(connected_person.id)

def sync_social_connections():
    out_game_obsolete_connections()
    create_missing_connections()
