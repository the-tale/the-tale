# coding: utf-8


from common.utils import testcase

from game.logic import create_test_map

from game.persons.storage import PersonsStorage
from game.persons.models import PERSON_STATE

from game.persons.tests.helpers import create_person

class PlacesStorageTest(testcase.TestCase):

    def setUp(self):
        super(PlacesStorageTest, self).setUp()
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

    def test_all_without_removed_records(self):
        self.assertEqual(len(self.storage.all()), 12)
        self.pers3._model.state = PERSON_STATE.REMOVED
        self.pers3.save()
        self.storage.sync(force=True)
        self.assertEqual(len(self.storage.all()), 11)
        self.assertFalse(self.pers3.id in self.storage)

    def test_remove_old_persons(self):
        self.assertEqual(len(self.storage.all()), 12)
        old_version = self.storage.version
        self.storage.remove_out_game_persons()
        self.assertNotEqual(old_version, self.storage.version)
        self.storage.save_all()
        self.storage.sync(force=True)
        self.assertEqual(len(self.storage.all()), 8)
