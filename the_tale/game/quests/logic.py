# -*- coding: utf-8 -*-
import random

from django.utils.log import getLogger

from dext.utils.decorators import retry_on_exception

from game.balance import constants as c

from game.map.places.storage import places_storage
from game.persons.storage import persons_storage
from game.map.roads.storage import waymarks_storage

from game.persons.models import PERSON_STATE

from game.prototypes import TimePrototype


from game.quests.quests_generator.quests_source import BaseQuestsSource
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.exceptions import RollBackException
from game.quests.quests_builders import QUESTS
from game.quests.writer import Writer
from game.quests.environment import Environment
from game.quests.prototypes import QuestPrototype
from game.quests.conf import quests_settings

_quests_logger=getLogger('the-tale.quests')

class QuestsSource(BaseQuestsSource):
    quests_list = QUESTS


def _fill_places_for_first_quest(base, hero):
    best_distance = waymarks_storage.average_path_length * 2
    best_destination = None

    for place in places_storage.all():
        if place.id == hero.position.place.id:
            continue
        path_length = waymarks_storage.look_for_road(hero.position.place, place).length
        if path_length < best_distance:
            best_distance = path_length
            best_destination = place

    base.add_place('place_%d' % best_destination.id, terrains=best_destination.terrains, external_data={'id': best_destination.id})
    base.add_place('place_%d' % hero.position.place.id, terrains=hero.position.place.terrains, external_data={'id': hero.position.place.id})


def _fill_places_for_short_paths(base, hero):
    for place in places_storage.all():
        if place.id != hero.position.place.id:
            path_length = waymarks_storage.look_for_road(hero.position.place, place).length
            #TODO: check, that every city has road less then average path length
            if path_length > waymarks_storage.average_path_length:
                continue

        place_uuid = 'place_%d' % place.id
        base.add_place(place_uuid, terrains=place.terrains, external_data={'id': place.id})


def get_knowlege_base(hero):

    base = KnowlegeBase()

    # fill places
    if hero.statistics.quests_done == 0:
        _fill_places_for_first_quest(base, hero)
    elif hero.is_short_quest_path_required:
        _fill_places_for_short_paths(base, hero)
    else:
        pass

    if len(base.places) < 2:
        for place in places_storage.all():
            place_uuid = 'place_%d' % place.id
            if place_uuid not in base.places:
                base.add_place(place_uuid, terrains=place.terrains, external_data={'id': place.id})


    # fill persons
    for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):
        person_uuid = 'person_%d' % person.id
        place_uuid = 'place_%d' % person.place_id

        if place_uuid not in base.places:
            continue

        base.add_person(person_uuid,
                        place=place_uuid,
                        profession=person.type.value,
                        external_data={'id': person.id,
                                       'name': person.name,
                                       'type': person.type.value,
                                       'gender': person.gender,
                                       'race': person.race,
                                       'mastery_verbose': person.mastery_verbose,
                                       'place_id': person.place_id})

    pref_mob = hero.preferences.mob
    if pref_mob:
        base.add_special('hero_pref_mob', {'id': pref_mob.uuid,
                                           'terrain': pref_mob.terrains})

    pref_place = hero.preferences.place
    place_uuid = 'place_%d' % pref_place.id if pref_place is not None else None
    if place_uuid in base.places:
        base.add_special('hero_pref_hometown', {'uuid': place_uuid})

    pref_friend = hero.preferences.friend
    friend_uuid = 'person_%d' % pref_friend.id if pref_friend is not None else None
    if friend_uuid in base.persons:
        base.add_special('hero_pref_friend', {'uuid': friend_uuid})

    pref_enemy = hero.preferences.enemy
    enemy_uuid = 'person_%d' % pref_enemy.id if pref_enemy is not None else None
    if enemy_uuid in base.persons:
        base.add_special('hero_pref_enemy', {'uuid': enemy_uuid})

    pref_equipment_slot = hero.preferences.equipment_slot
    if pref_equipment_slot:
        base.add_special('hero_pref_equipment_slot', pref_equipment_slot)

    base.initialize()

    return base


def create_random_quest_for_hero(hero):

    special = (c.QUESTS_SPECIAL_FRACTION > random.uniform(0, 1))

    knowlege_base = get_knowlege_base(hero)

    if special:
        try:
            return _create_random_quest_for_hero(hero, knowlege_base, special=True)
        except RollBackException:
            pass

    return _create_random_quest_for_hero(hero, knowlege_base, special=False)


@retry_on_exception(max_retries=quests_settings.MAX_QUEST_GENERATION_RETRIES, exceptions=[RollBackException])
def _create_random_quest_for_hero(hero, knowlege_base, special):

    quests_source = QuestsSource()

    env = Environment(writers_constructor=Writer,
                      quests_source=quests_source,
                      knowlege_base=knowlege_base)

    hero_position_uuid = 'place_%d' % hero.position.place.id # expecting place, not road
    env.new_place(place_uuid=hero_position_uuid) #register first place

    current_time = TimePrototype.get_current_turn_number()

    excluded_quests = []
    for quest_type, turn_number in hero.quests_history.items():
        if turn_number + c.QUESTS_LOCK_TIME.get(quest_type, 0) >= current_time:
            excluded_quests.append(quest_type)

    if special:
        env.new_quest(from_list=hero.get_special_quests(), excluded_list=excluded_quests, place_start=hero_position_uuid)
    else:
        quests_list = set([quest.type() for quest in quests_source.quests_list]) - set(['hunt', 'hometown', 'helpfriend', 'interfereenemy', 'searchsmith'])
        env.new_quest(from_list=quests_list, excluded_list=excluded_quests, place_start=hero_position_uuid)

    env.create_lines()

    if not env.root_quest.available:
        raise RollBackException('quest is not available')

    env.sync()

    quest_prototype = QuestPrototype.create(hero, env)

    _quests_logger.info('hero: %d\n\n\n%s' % (hero.id, quest_prototype._model.env))

    return quest_prototype
