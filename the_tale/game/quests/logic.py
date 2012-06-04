# -*- coding: utf-8 -*-

from dext.utils.decorators import retry_on_exception

from ..map.places.models import Place
from ..map.places.prototypes import get_place_by_model

from .quests_generator.lines import BaseQuestsSource
from .quests_generator.knowlege_base import KnowlegeBase
from .quests_generator.exceptions import RollBackException
from .writer import Writer

from .environment import Environment
from .prototypes import QuestPrototype

def get_knowlege_base():

    base = KnowlegeBase()

    # fill base
    for place_model in Place.objects.all():
        place = get_place_by_model(place_model)

        place_uuid = 'place_%d' % place.id

        base.add_place(place_uuid, external_data={'id': place.id,
                                                  'name': place.name})

        for person in place.persons:
            person_uuid = 'person_%d' % person.id
            base.add_person(person_uuid, place=place_uuid, external_data={'id': person.id,
                                                                          'name': person.name,
                                                                          'type': person.type})

    base.initialize()

    return base


@retry_on_exception(RollBackException)
def create_random_quest_for_hero(hero):

    base = get_knowlege_base()

    env = Environment(quests_source=BaseQuestsSource(),
                      writers_constructor=Writer,
                      knowlege_base=base)

    hero_position_uuid = 'place_%d' % hero.position.place.id # expecting place, not road
    env.new_place(place_uuid=hero_position_uuid) #register first place

    env.new_quest(place_start=hero_position_uuid)
    env.create_lines()

    quest_prototype = QuestPrototype.create(hero, env)

    return quest_prototype
