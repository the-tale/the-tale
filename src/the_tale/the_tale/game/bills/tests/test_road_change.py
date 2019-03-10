
import smart_imports

smart_imports.all()


class RoadChangeTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super().setUp()

        self.new_path = 'rddr'

        self.old_road = roads_logic.road_between_places(self.place1, self.place2)

        self.assertNotEqual(self.new_path, self.old_road.path)

        self.bill_data = bills.road_change.RoadChange(place_1_id=self.place1.id,
                                                      place_2_id=self.place2.id,
                                                      path=self.new_path)

        self.bill = prototypes.BillPrototype.create(self.account1,
                                                    'bill-1-caption', self.bill_data,
                                                    chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_1_id, self.place1.id)
        self.assertEqual(self.bill.data.place_2_id, self.place2.id)
        self.assertEqual(self.bill.data.path, self.new_path)

        self.assertEqual(self.bill.data.old_place_1_name_forms, self.place1.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name_forms, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_path, self.old_road.path)

        self.assertEqual(self.bill.data.place_1.id, self.place1.id)
        self.assertEqual(self.bill.data.place_2.id, self.place2.id)

        self.assertEqual(self.bill.data.old_place_1_name, self.place1.utg_name.normal_form())
        self.assertEqual(self.bill.data.old_place_2_name, self.place2.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_1_name_changed)
        self.assertFalse(self.bill.data.place_2_name_changed)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials(),
                         {'place_1': self.bill.data.place_1_id,
                          'place_2': self.bill.data.place_2_id,
                          'path': self.bill.data.path})

    def test_actors(self):
        self.assertEqual(set(id(a) for a in self.bill_data.actors), set([id(self.place1), id(self.place2)]))

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place_1': self.place2.id,
                                                         'place_2': self.place3.id,
                                                         'path': 'luld'})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        old_road = roads_logic.road_between_places(self.place2, self.place3)

        self.assertEqual(self.bill.data.place_1_id, self.place2.id)
        self.assertEqual(self.bill.data.place_2_id, self.place3.id)
        self.assertEqual(self.bill.data.path, 'luld')

        self.assertEqual(self.bill.data.old_place_1_name_forms, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name_forms, self.place3.utg_name)
        self.assertEqual(self.bill.data.old_path, old_road.path)

        self.assertEqual(self.bill.data.place_1.id, self.place2.id)
        self.assertEqual(self.bill.data.place_2.id, self.place3.id)

        self.assertEqual(self.bill.data.old_place_1_name, self.place2.utg_name.normal_form())
        self.assertEqual(self.bill.data.old_place_2_name, self.place3.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_2_name_changed)
        self.assertFalse(self.bill.data.place_1_name_changed)

    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place2.id,
                                                         'path': self.new_path})
        self.assertTrue(form.is_valid())

    def test_user_form_validation__not_exists(self):
        self.assertEqual(roads_logic.road_between_places(self.place1, self.place3), None)
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place3.id,
                                                         'path': 'rdrd'})
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.roads.logic.is_path_suitable_for_road',
                lambda **kwargs: roads_relations.ROAD_PATH_ERRORS.random(exclude=[roads_relations.ROAD_PATH_ERRORS.NO_ERRORS]))
    def test_user_form_validation__bad_path(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place2.id,
                                                         'path': self.new_path})
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def apply_bill(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

    def test_apply(self):

        old_storage_version = roads_storage.roads._version

        with self.check_not_changed(lambda: len(roads_storage.roads.all())):
            self.apply_bill()

        self.assertNotEqual(old_storage_version, roads_storage.roads._version)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        road = roads_logic.road_between_places(self.place1, self.place2)

        self.assertEqual(road.path, self.new_path)

    def test_has_meaning__not_exists(self):
        bill_data = bills.road_change.RoadChange(place_1_id=self.place1.id,
                                                 place_2_id=self.place3.id,
                                                 path='rdrd')

        bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data,
                                               chronicle_on_accepted='chronicle-on-accepted')

        self.assertFalse(bill.has_meaning())

    @mock.patch('the_tale.game.roads.logic.is_path_suitable_for_road',
                lambda **kwargs: roads_relations.ROAD_PATH_ERRORS.random(exclude=[roads_relations.ROAD_PATH_ERRORS.NO_ERRORS]))
    def test_has_meaning__wrong_path(self):
        bill_data = bills.road_change.RoadChange(place_1_id=self.place1.id,
                                                 place_2_id=self.place2.id,
                                                 path=self.new_path)

        bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data,
                                               chronicle_on_accepted='chronicle-on-accepted')

        self.assertFalse(bill.has_meaning())
