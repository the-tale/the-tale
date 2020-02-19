
import smart_imports

smart_imports.all()


def tt_power_impacts(person_inner_circle, place_inner_circle, actor_type, actor_id, person, amount, fame):
    power_multiplier = 1

    if person.has_building:
        power_multiplier += c.BUILDING_PERSON_POWER_BONUS

    # this power will go to person and to place
    place_power = amount * power_multiplier

    # this power, only to person
    person_power = round(amount * power_multiplier * person.place.attrs.freedom)

    impact_types = [game_tt_services.IMPACT_TYPE.OUTER_CIRCLE]

    if person_inner_circle:
        impact_types.append(game_tt_services.IMPACT_TYPE.INNER_CIRCLE)

    for impact_type in impact_types:
        yield game_tt_services.PowerImpact(type=impact_type,
                                           actor_type=actor_type,
                                           actor_id=actor_id,
                                           target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                           target_id=person.id,
                                           amount=person_power)

    yield from places_logic.tt_power_impacts(inner_circle=place_inner_circle,
                                             actor_type=actor_type,
                                             actor_id=actor_id,
                                             place=person.place,
                                             amount=place_power,
                                             fame=fame * person.attrs.places_help_amount)

    if not person_inner_circle:
        return

    target_type = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE

    if amount < 0:
        target_type = tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE

    yield game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                       actor_type=actor_type,
                                       actor_id=actor_id,
                                       target_type=target_type,
                                       target_id=person.id,
                                       amount=abs(person_power))


def impacts_from_hero(hero, person, power, inner_circle_places, inner_circle_persons, impacts_generator=tt_power_impacts):
    person_power = 0
    partner_power = 0
    concurrent_power = 0

    partner_fame = c.HERO_FAME_PER_HELP * person.attrs.social_relations_partners_power_modifier
    concurrent_fame = c.HERO_FAME_PER_HELP * person.attrs.social_relations_concurrents_power_modifier

    can_change_power = hero.can_change_person_power(person)

    person_power = hero.modify_politics_power(power, person=person)

    partner_power = person_power * person.attrs.social_relations_partners_power_modifier
    concurrent_power = -person_power * person.attrs.social_relations_concurrents_power_modifier

    has_person_in_preferences = hero.preferences.has_person_in_preferences(person) or (person.id in inner_circle_persons)
    has_place_in_preferences = hero.preferences.has_place_in_preferences(person.place) or (person.place_id in inner_circle_places)

    yield from impacts_generator(person_inner_circle=has_person_in_preferences,
                                 place_inner_circle=has_place_in_preferences,
                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                 actor_id=hero.id,
                                 person=person,
                                 amount=person_power if can_change_power else 0,
                                 fame=c.HERO_FAME_PER_HELP if 0 < power else 0)

    for social_connection_type, connected_person_id in storage.social_connections.get_person_connections(person):
        connected_person = storage.persons[connected_person_id]

        connected_power = partner_power if social_connection_type.is_PARTNER else concurrent_power
        connected_fame = partner_fame if social_connection_type.is_PARTNER else concurrent_fame

        can_change_connected_power = hero.can_change_person_power(connected_person)

        yield from impacts_generator(person_inner_circle=has_person_in_preferences,
                                     place_inner_circle=has_place_in_preferences,
                                     actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                     actor_id=hero.id,
                                     person=connected_person,
                                     amount=connected_power if can_change_connected_power else 0,
                                     fame=connected_fame if 0 < connected_power else 0)


def save_person(person, new=False):

    data = {'name': person.utg_name.serialize(),
            'job': person.job.serialize(),
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
        person.place.persons_changed_at_turn = game_turn.number()

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
                            created_at_turn=game_turn.number(),
                            updated_at_turn=game_turn.number(),
                            updated_at=datetime.datetime.now(),
                            place_id=place.id,
                            gender=gender,
                            race=race,
                            type=type,
                            attrs=attributes.Attributes(),
                            personality_cosmetic=personality_cosmetic,
                            personality_practical=personality_practical,
                            utg_name=utg_name,
                            job=jobs_logic.create_job(jobs.PersonJob),
                            moved_at_turn=game_turn.number())
    person.refresh_attributes()
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
                          utg_name=utg_words.Word.deserialize(data['name']),
                          job=jobs.PersonJob.deserialize(data['job']),
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
                                    created_at_turn=model.created_at_turn)


def create_social_connection(connection_type, person_1, person_2):

    if person_1.id > person_2.id:
        person_1, person_2 = person_2, person_1

    if storage.social_connections.is_connected(person_1, person_2):
        raise exceptions.PersonsAlreadyConnectedError(person_1_id=person_1.id, person_2_id=person_2.id)

    model = models.SocialConnection.objects.create(created_at_turn=game_turn.number(),
                                                   person_1_id=person_1.id,
                                                   person_2_id=person_2.id,
                                                   connection=connection_type)

    connection = social_connection_from_model(model)

    storage.social_connections.add_item(connection.id, connection)
    storage.social_connections.update_version()

    return connection


def remove_connection(connection):
    models.SocialConnection.objects.filter(id=connection.id).delete()
    storage.social_connections.update_version()
    storage.social_connections.refresh()


def move_person_to_place(person, new_place):
    person.place_id = new_place.id
    person.moved_at_turn = game_turn.number()

    save_person(person)


def api_show_url(person):
    arguments = {'api_version': conf.settings.API_SHOW_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:persons:api-show', person.id, **arguments)


def refresh_all_persons_attributes():
    for person in storage.persons.all():
        person.refresh_attributes()
        save_person(person)
