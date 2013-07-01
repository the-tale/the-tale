# coding: utf-8

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.chronicle.models import Actor, RecordToActor, Record
from game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE
from game.chronicle.prototypes import create_external_actor, RecordToActorPrototype, RecordPrototype
from game.chronicle.tests.helpers import FakeRecord


class RecordPrototypeTests(TestCase):

    def setUp(self):
        super(RecordPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def test_create_actors_connections_created(self):
        old_connections_number = RecordToActor.objects.all().count()
        FakeRecord(type_=RECORD_TYPE.PLACE_CHANGE_RACE,
                   actors=[(ACTOR_ROLE.PLACE, create_external_actor(self.place_1)),
                           (ACTOR_ROLE.PERSON, create_external_actor(self.place_1.persons[0]))]).create_record()
        self.assertEqual(old_connections_number + 2, RecordToActor.objects.all().count())

    def test_get_actor_records_query(self):
        self.assertTrue(Record.objects.all().exists())

        records_ids = RecordPrototype.get_actor_records_query(self.place_1).values_list('id', flat=True)
        actor = Actor.objects.get(place_id=self.place_1.id)

        for record in Record.objects.all():
            if actor.id in record.actors.all().values_list('id', flat=True):
                self.assertTrue(record.id in records_ids)
            else:
                self.assertFalse(record.id in records_ids)

    def test_get_last_actor_records(self):
        records = RecordPrototype.get_last_actor_records(self.place_1, 10000)
        self.assertTrue(len(records) < 10000)
        for i, record in enumerate(records[:-1]):
            self.assertTrue(record._model.created_at > records[i+1]._model.created_at)


class RecordToActorPrototypeTests(TestCase):

    def setUp(self):
        super(RecordToActorPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def test_actor_not_created_second_time(self):
        external_actor = create_external_actor(self.place_3)
        self.assertEqual(Actor.objects.filter(uid=external_actor.uid).count(), 1)
        record = FakeRecord(type_=RECORD_TYPE.PLACE_CHANGE_RACE, index=0, turn_number=0).create_record()
        RecordToActorPrototype.create(ACTOR_ROLE.PLACE, record, external_actor)
        self.assertEqual(Actor.objects.filter(uid=external_actor.uid).count(), 1)
