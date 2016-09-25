# coding: utf-8

import random

from the_tale.game import names

from the_tale.game.relations import GENDER, RACE

from .. import logic
from the_tale.game.persons.relations import PERSON_TYPE


def create_person(place):
    race = random.choice(RACE.records)
    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
    return logic.create_person(place,
                               race=race,
                               type=random.choice(PERSON_TYPE.records),
                               utg_name=names.generator.get_name(race, gender),
                               gender=gender)
