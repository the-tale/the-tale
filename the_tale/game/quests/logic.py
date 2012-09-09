# -*- coding: utf-8 -*-
import random

from dext.utils.decorators import retry_on_exception

from game.balance import constants as c

from game.map.places.storage import places_storage
from game.persons.storage import persons_storage

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


class QuestsSource(BaseQuestsSource):
    quests_list = QUESTS


def get_knowlege_base(hero):

    base = KnowlegeBase()

    # fill base
    for place in places_storage.all():
        place_uuid = 'place_%d' % place.id
        base.add_place(place_uuid, terrain=place.terrain, external_data={'id': place.id})

    for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):
        person_uuid = 'person_%d' % person.id
        place_uuid = 'place_%d' % person.place_id
        base.add_person(person_uuid, place=place_uuid, external_data={'id': person.id,
                                                                      'name': person.name,
                                                                      'type': person.type,
                                                                      'gender': person.gender,
                                                                      'race': person.race,
                                                                      'place_id': person.place_id})

    pref_mob = hero.preferences.mob
    if pref_mob:
        base.add_special('hero_pref_mob', {'id': pref_mob.id,
                                           'terrain': pref_mob.terrain})

    pref_place = hero.preferences.get_place()
    if pref_place:
        place_uuid = 'place_%d' % pref_place.id
        base.add_special('hero_pref_hometown', {'uuid': place_uuid})

    pref_friend = hero.preferences.get_friend()
    if pref_friend:
        friend_uuid = 'person_%d' % pref_friend.id
        base.add_special('hero_pref_friend', {'uuid': friend_uuid})

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

    env = Environment(writers_constructor=Writer,
                      quests_source=QuestsSource(),
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
        env.new_quest(excluded_list=excluded_quests, place_start=hero_position_uuid)

    env.create_lines()

    env.sync()

    quest_prototype = QuestPrototype.create(hero, env)

    return quest_prototype
