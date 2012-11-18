# coding: utf-8

import random

from game import names

from game.game_info import RACE, GENDER

from game.persons.prototypes import PersonPrototype
from game.persons.models import PERSON_TYPE_CHOICES

def create_person(place, state):
    race = random.choice(RACE.CHOICES)[0]
    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
    return PersonPrototype.create(place,
                                  state=state,
                                  race=race,
                                  tp=random.choice(PERSON_TYPE_CHOICES)[0],
                                  name=names.generator.get_name(race, gender),
                                  gender=gender,
                                  power=0)
