# coding: utf-8

from django.test import TestCase

from game.logic import create_test_map

from game.persons.storage import PersonsStorage
from game.persons.models import PERSON_STATE

from game.persons.tests.helpers import create_person

class PlacesStorageTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        self.pers1 = create_person(self.p1, PERSON_STATE.OUT_GAME)
        self.pers2 = create_person(self.p2, PERSON_STATE.OUT_GAME)
        self.pers3 = create_person(self.p3, PERSON_STATE.OUT_GAME)
        self.pers3 = create_person(self.p3, PERSON_STATE.OUT_GAME)

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
