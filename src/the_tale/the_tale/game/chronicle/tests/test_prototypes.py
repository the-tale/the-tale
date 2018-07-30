
import smart_imports

smart_imports.all()


class RecordPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(RecordPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()
        self.account = self.accounts_factory.create_account()

    def test_create_actors_connections_created(self):
        old_connections_number = models.RecordToActor.objects.all().count()
        helpers.FakeRecord(type_=relations.RECORD_TYPE.PLACE_CHANGE_RACE,
                           actors=[(relations.ACTOR_ROLE.PLACE, prototypes.create_external_actor(self.place_1)),
                                   (relations.ACTOR_ROLE.PERSON, prototypes.create_external_actor(self.place_1.persons[0]))]).create_record()
        self.assertEqual(old_connections_number + 2, models.RecordToActor.objects.all().count())

    def test_get_last_actor_records(self):
        records = prototypes.RecordPrototype.get_last_actor_records(self.place_1, 10000)
        self.assertTrue(len(records) < 10000)
        for i, record in enumerate(records[:-1]):
            self.assertTrue(record._model.created_at > records[i + 1]._model.created_at)
