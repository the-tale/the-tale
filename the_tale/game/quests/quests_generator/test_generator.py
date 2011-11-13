# coding: utf-8

from .lines import BaseQuestsSource, BaseWritersSouece
from .knowlege_base import KnowlegeBase

from .environment import BaseEnvironment

def get_knowlege_base():

    base = KnowlegeBase()

    for place_number in xrange(5):
        place_uuid = 'place_%d' % place_number
        base.add_place(place_uuid)

        for person_number in xrange(5):
            base.add_person('person_%d_%d' % (place_number, person_number), place=place_uuid)

    base.initialize()

    return base
    

def create_random_quest():

    base = get_knowlege_base()

    env = BaseEnvironment(quests_source=BaseQuestsSource(),
                          writers_source=BaseWritersSouece(),
                          knowlege_base=base)

    env.new_quest()
    env.create_lines()

    return env
