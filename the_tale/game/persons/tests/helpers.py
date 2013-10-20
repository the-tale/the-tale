# coding: utf-8

import random

from game import names

from game.relations import GENDER, RACE

from game.persons.prototypes import PersonPrototype
from game.persons.relations import PERSON_TYPE

def create_person(place, state):
    race = random.choice(RACE._records)
    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
    return PersonPrototype.create(place,
                                  state=state,
                                  race=race,
                                  tp=random.choice(PERSON_TYPE._records),
                                  name=names.generator.get_name(race, gender),
                                  gender=gender)
