
import random
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game import turn
from the_tale.game import tt_api_impacts

from the_tale.game.jobs import objects as jobs_objects
from the_tale.game.jobs import effects as jobs_effects
from the_tale.game.jobs import logic as jobs_logic

from the_tale.game.politic_power import conf as politic_power_conf
from the_tale.game.politic_power import logic as politic_power_logic
from the_tale.game.politic_power import storage as politic_power_storage

from the_tale.game import effects

from . import races
from . import conf
from . import models
from . import objects
from . import habits
from . import attributes
from . import modifiers
from . import relations


EffectsContainer = effects.create_container(relations.ATTRIBUTE)


class PlaceJob(jobs_objects.Job):
    ACTOR = 'place'

    ACTOR_TYPE = tt_api_impacts.OBJECT_TYPE.PLACE
    POSITIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE
    NEGATIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE

    # умножаем на 2, так как кажая остановка в городе, по сути, даёт влияние в 2-кратном размере
    # Город получит влияние и от задания, которое герой выполнил и от того, которое возьмёт
    NORMAL_POWER = f.normal_job_power(politic_power_conf.settings.PLACE_INNER_CIRCLE_SIZE) * 2

    def load_power(self, actor_id):
        return politic_power_logic.get_job_power(place_id=actor_id)

    def load_inner_circle(self, actor_id):
        return politic_power_logic.get_inner_circle(place_id=actor_id)

    def get_job_power(self, actor_id):
        from the_tale.game.places import storage

        current_place = storage.places[actor_id]

        return jobs_logic.job_power(power=politic_power_storage.places.total_power_fraction(current_place.id),
                                    powers=[politic_power_storage.places.total_power_fraction(place.id)
                                            for place in current_place.get_same_places()])

    def get_project_name(self, actor_id):
        from the_tale.game.places import storage
        name = storage.places[actor_id].utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        return 'Проект города {name}'.format(name=name)

    def get_objects(self, actor_id):
        from the_tale.game.places import storage

        return {'person': None,
                'place': storage.places[actor_id]}

    def get_effects_priorities(self, actor_id):
        return {effect: 1 for effect in jobs_effects.EFFECT.records}


def tt_power_impacts(inner_circle, actor_type, actor_id, place, amount):
    amount *= place.attrs.freedom

    impact_type = tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE

    if inner_circle:
        impact_type = tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE

    yield tt_api_impacts.PowerImpact(type=impact_type,
                                     actor_type=actor_type,
                                     actor_id=actor_id,
                                     target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                     target_id=place.id,
                                     amount=amount)

    if not inner_circle:
        return

    target_type = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE

    if amount < 0:
        target_type = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE

    yield tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                     actor_type=actor_type,
                                     actor_id=actor_id,
                                     target_type=target_type,
                                     target_id=place.id,
                                     amount=abs(amount))


def load_place(place_id=None, place_model=None):
    try:
        if place_id is not None:
            place_model = models.Place.objects.get(id=place_id)
        elif place_model is None:
            return None
    except models.Place.DoesNotExist:
        return None

    data = s11n.from_json(place_model.data)

    if 'nearest_cells' in data:
        data['nearest_cells'] = list(map(tuple, data['nearest_cells']))

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
                          utg_name=utg_words.Word.deserialize(data['name']),
                          attrs=attributes.Attributes.deserialize(data.get('attributes', {})),
                          races=races.Races.deserialize(data['races']),
                          nearest_cells=data.get('nearest_cells', []),
                          effects=EffectsContainer.deserialize(data.get('effects')),
                          job=PlaceJob.deserialize(data['job']),
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
            'job': place.job.serialize()}

    arguments = {'x': place.x,
                 'y': place.y,
                 'updated_at_turn': turn.number(),
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
        place_model = models.Place.objects.create(created_at_turn=turn.number(), **arguments)
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
                          updated_at_turn=turn.number(),
                          created_at=datetime.datetime.now(),
                          created_at_turn=turn.number(),
                          habit_honor=habits.Honor(raw_value=0),
                          habit_honor_positive=0,
                          habit_honor_negative=0,
                          habit_peacefulness=habits.Peacefulness(raw_value=0),
                          habit_peacefulness_positive=0,
                          habit_peacefulness_negative=0,
                          is_frontier=is_frontier,
                          description='',
                          race=race,
                          persons_changed_at_turn=turn.number(),
                          attrs=attributes.Attributes(size=size),
                          utg_name=utg_name,
                          races=races.Races(),
                          nearest_cells=[],
                          effects=EffectsContainer(),
                          job=jobs_logic.create_job(PlaceJob),
                          modifier=modifiers.CITY_MODIFIERS.NONE)
    place.refresh_attributes()
    save_place(place, new=True)
    return place


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


def get_available_positions(center_x, center_y, building_position_radius=c.BUILDING_POSITION_RADIUS): # pylint: disable=R0914
    from the_tale.game.places import storage
    from the_tale.game.roads.storage import roads_storage
    from the_tale.game.roads.relations import PATH_DIRECTION
    from the_tale.game.map.conf import map_settings

    positions = set()

    for i in range(0, building_position_radius+1):
        for j in range(0, building_position_radius+1):
            positions.add((center_x+i, center_y+j))
            positions.add((center_x-i, center_y+j))
            positions.add((center_x+i, center_y-j))
            positions.add((center_x-i, center_y-j))

    positions =  set(pos for pos in positions
                     if 0 <= pos[0] < map_settings.WIDTH and 0 <= pos[1] < map_settings.HEIGHT)

    removed_positions = set()

    for place in storage.places.all():
        removed_positions.add((place.x, place.y))

    for building in storage.buildings.all():
        removed_positions.add((building.x, building.y))

    for road in roads_storage.all_exists_roads():
        x, y = road.point_1.x, road.point_1.y
        for direction in road.path:
            if direction == PATH_DIRECTION.LEFT.value: x -= 1
            elif direction == PATH_DIRECTION.RIGHT.value: x += 1
            elif direction == PATH_DIRECTION.UP.value: y -= 1
            elif direction == PATH_DIRECTION.DOWN.value: y += 1

            removed_positions.add((x, y))

    result = positions - removed_positions

    return result if result else get_available_positions(center_x, center_y, building_position_radius=building_position_radius+1)


def create_building(person, utg_name, position=None):
    from the_tale.game.places import storage

    building = storage.buildings.get_by_person_id(person.id)

    if building:
        return building

    # remove any destroyed buildings for person
    models.Building.objects.filter(person_id=person.id).delete()

    if position is None:
        position = random.choice(list(get_available_positions(person.place.x, person.place.y)))

    x, y = position

    building = objects.Building(id=None,
                                x=x,
                                y=y,
                                type=person.type.building_type,
                                integrity=1.0,
                                created_at_turn=turn.number(),
                                state=relations.BUILDING_STATE.WORKING,
                                utg_name=utg_name,
                                person_id=person.id)

    save_building(building, new=True)

    return building


def save_building(building, new=False):
    from the_tale.game.places import storage

    data = {'name': building.utg_name.serialize()}

    arguments = {'x': building.x,
                 'y': building.y,
                 'created_at_turn': building.created_at_turn,
                 'state': building.state,
                 'type': building.type,
                 'integrity': building.integrity,
                 'place_id': building.place.id,
                 'person_id': building.person.id,
                 'data': s11n.to_json(data)}

    if new:
        building_model = models.Building.objects.create(**arguments)
        building.id = building_model.id
        storage.buildings.add_item(building.id, building)
    else:
        models.Building.objects.filter(id=building.id).update(**arguments)

    storage.buildings.update_version()


def load_building(building_id=None, building_model=None):
    try:
        if building_id is not None:
            building_model = models.Building.objects.get(id=building_id)
        elif building_model is None:
            return None
    except models.Building.DoesNotExist:
        return None

    data = s11n.from_json(building_model.data)

    building = objects.Building(id=building_model.id,
                                x=building_model.x,
                                y=building_model.y,
                                created_at_turn=building_model.created_at_turn,
                                utg_name=utg_words.Word.deserialize(data['name']),
                                type=building_model.type,
                                integrity=building_model.integrity,
                                state=building_model.state,
                                person_id=building_model.person_id)

    return building


def destroy_building(building):
    from the_tale.game.places import storage

    building.state = relations.BUILDING_STATE.DESTROYED
    save_building(building)

    storage.buildings.update_version()
    storage.buildings.refresh()


def sync_sizes(places, hours, max_economic):
    if not places:
        return

    places = sorted(places, key=lambda place: politic_power_storage.places.total_power_fraction(place.id))
    places_number = len(places)

    for i, place in enumerate(places):
        place.attrs.set_power_economic(int(max_economic * float(i) / places_number) + 1)
        place.attrs.sync_size(hours)
