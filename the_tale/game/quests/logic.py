# -*- coding: utf-8 -*-
import random

from dext.utils.decorators import retry_on_exception

from game.balance import constants as c

from game.map.places.models import Place
from game.map.places.prototypes import get_place_by_model

from game.quests.quests_generator.lines import BaseQuestsSource
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.exceptions import RollBackException
from game.quests.writer import Writer
from game.quests.environment import Environment
from game.quests.prototypes import QuestPrototype

def get_knowlege_base(hero):

    base = KnowlegeBase()

    # fill base
    for place_model in Place.objects.all():
        place = get_place_by_model(place_model)

        place_uuid = 'place_%d' % place.id

        base.add_place(place_uuid, terrain=place.terrain, external_data={'id': place.id})

        for person in place.persons:
            person_uuid = 'person_%d' % person.id
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

    base.initialize()

    return base


@retry_on_exception(RollBackException)
def create_random_quest_for_hero(current_time, hero):

    base = get_knowlege_base(hero)

    env = Environment(quests_source=BaseQuestsSource(),
                      writers_constructor=Writer,
                      knowlege_base=base)

    hero_position_uuid = 'place_%d' % hero.position.place.id # expecting place, not road
    env.new_place(place_uuid=hero_position_uuid) #register first place

    special = (c.QUESTS_SPECIAL_FRACTION > random.uniform(0, 1))

    env.new_quest(place_start=hero_position_uuid, special=special)
    env.create_lines()

    env.sync()

    quest_prototype = QuestPrototype.create(current_time, hero, env)

    return quest_prototype
