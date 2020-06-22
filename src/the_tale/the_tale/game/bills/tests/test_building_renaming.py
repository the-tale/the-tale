
import smart_imports

smart_imports.all()


class BuildingRenamingTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(BuildingRenamingTests, self).setUp()

        self.person_1 = self.place1.persons[0]
        self.person_2 = self.place2.persons[0]
        self.person_3 = self.place3.persons[0]

        self.building = places_logic.create_building(self.person_1, utg_name=game_names.generator().get_test_name('building-name'))
        self.building_2 = places_logic.create_building(self.person_2, utg_name=game_names.generator().get_test_name('building-name-2'))

        self.bill_data = bills.building_renaming.BuildingRenaming(person_id=self.person_1.id,
                                                                  old_place_name_forms=self.place1.utg_name,
                                                                  new_building_name_forms=game_names.generator().get_test_name('new-building-name'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-caption', self.bill_data, chronicle_on_accepted='chronicle-accepted-1')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)
        self.assertEqual(self.bill.data.old_name, 'building-name-нс,ед,им')
        self.assertEqual(self.bill.data.new_name, 'new-building-name-нс,ед,им')

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person_1.place), id(self.person_1)])

    def test_update(self):
        data = linguistics_helpers.get_word_post_data(game_names.generator().get_test_name('new-building-name-2'), prefix='name')
        data.update({'caption': 'new-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'person': self.person_2.id})
        form = self.bill.data.get_user_form_update(post=data)
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)
        self.assertEqual(self.bill.data.old_name, 'building-name-2-нс,ед,им')
        self.assertEqual(self.bill.data.new_name, 'new-building-name-2-нс,ед,им')

    def test_user_form_choices(self):
        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id})

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)

        self.assertEqual(set(persons_ids), set([self.person_1.id, self.person_2.id]))

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('r-building-name')

        data = {'person': self.person_1.id,
                'chronicle_on_accepted': 'chronicle-accepted-1',
                'caption': 'bill-caption'}
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True

        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertEqual(places_models.Building.objects.filter(state=places_relations.BUILDING_STATE.WORKING).count(), 2)

        building = places_logic.load_building(self.building.id)

        self.assertEqual(building.name, 'r-building-name-нс,ед,им')

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_is_make_sense__same_name(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('r-building-name')

        data = {'person': self.person_1.id,
                'chronicle_on_accepted': 'chronicle-accepted-1',
                'caption': 'bill-caption'}
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True

        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        self.bill.state = relations.BILL_STATE.VOTING
        self.bill.save()

        self.assertFalse(self.bill.has_meaning())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_no_building(self):

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('r-building-name')

        data = {'person': self.person_1.id,
                'chronicle_on_accepted': 'chronicle-accepted-1',
                'caption': 'bill-caption'}
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True

        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        places_logic.destroy_building(self.building)

        self.assertTrue(self.bill.apply())

        self.assertEqual(places_models.Building.objects.filter(state=places_relations.BUILDING_STATE.WORKING).count(), 1)

        building = places_logic.load_building(self.building.id)

        self.assertEqual(building.name, 'building-name-нс,ед,им')

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_is_make_sense__no_building(self):

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('r-building-name')

        data = {'person': self.person_1.id,
                'chronicle_on_accepted': 'chronicle-accepted-1',
                'caption': 'bill-caption'}
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True

        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        places_logic.destroy_building(self.building)

        self.assertFalse(self.bill.has_meaning())
