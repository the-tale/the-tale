# coding: utf-8

import random

from the_tale.game import names

from the_tale.game.relations import GENDER, RACE

from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.relations import PERSON_TYPE

def create_person(place, state):
    race = random.choice(RACE.records)
    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
    return PersonPrototype.create(place,
                                  state=state,
                                  race=race,
                                  tp=random.choice(PERSON_TYPE.records),
                                  name_forms=names.generator.get_name(race, gender),
                                  gender=gender)
