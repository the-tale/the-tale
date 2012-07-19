# coding: utf-8
import random

from django.test import TestCase

from dext.settings import settings

from game import names
from game.game_info import RACE_CHOICES, GENDER
from game.logic import create_test_map

from game.persons.models import Person
from game.persons.prototypes import PersonPrototype
from game.persons.storage import PersonsStorage
from game.persons.models import PERSON_TYPE_CHOICES, PERSON_STATE


class PlacesStorageTest(TestCase):

    def create_person(self, place, state):
        race = random.choice(RACE_CHOICES)[0]
        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
        return PersonPrototype.create(place,
                                      state=state,
                                      race=race,
                                      tp=random.choice(PERSON_TYPE_CHOICES)[0],
                                      name=names.generator.get_name(race, gender),
                                      gender=gender,
                                      power=0)

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        self.pers1 = self.create_person(self.p1, PERSON_STATE.OUT_GAME)
        self.pers2 = self.create_person(self.p2, PERSON_STATE.OUT_GAME)
        self.pers3 = self.create_person(self.p3, PERSON_STATE.OUT_GAME)
        self.pers3 = self.create_person(self.p3, PERSON_STATE.OUT_GAME)

        self.storage = PersonsStorage()
        self.storage.sync()

    def test_filter_none(self):
        self.assertEqual(len(self.storage.filter(666)), 0)

    def test_filter_out_game(self):
        self.assertEqual(len(self.storage.filter(state=PERSON_STATE.OUT_GAME)), 4)

    def test_filter_out_game_in_place(self):
        self.assertEqual(len(self.storage.filter(place_id=self.p1.id, state=PERSON_STATE.OUT_GAME)), 1)
        self.assertEqual(len(self.storage.filter(place_id=self.p2.id, state=PERSON_STATE.OUT_GAME)), 1)
        self.assertEqual(len(self.storage.filter(place_id=self.p3.id, state=PERSON_STATE.OUT_GAME)), 2)
