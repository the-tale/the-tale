# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.game.chronicle.models import RecordToActor
from the_tale.game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE
from the_tale.game.chronicle.prototypes import create_external_actor, RecordPrototype
from the_tale.game.chronicle.tests.helpers import FakeRecord


class RecordPrototypeTests(TestCase):

    def setUp(self):
        super(RecordPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()
        self.account = self.accounts_factory.create_account()

    def test_create_actors_connections_created(self):
        old_connections_number = RecordToActor.objects.all().count()
        FakeRecord(type_=RECORD_TYPE.PLACE_CHANGE_RACE,
                   actors=[(ACTOR_ROLE.PLACE, create_external_actor(self.place_1)),
                           (ACTOR_ROLE.PERSON, create_external_actor(self.place_1.persons[0]))]).create_record()
        self.assertEqual(old_connections_number + 2, RecordToActor.objects.all().count())

    def test_get_last_actor_records(self):
        records = RecordPrototype.get_last_actor_records(self.place_1, 10000)
        self.assertTrue(len(records) < 10000)
        for i, record in enumerate(records[:-1]):
            self.assertTrue(record._model.created_at > records[i+1]._model.created_at)
