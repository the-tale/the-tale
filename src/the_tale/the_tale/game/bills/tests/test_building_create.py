
import smart_imports

smart_imports.all()


class BuildingCreateTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(BuildingCreateTests, self).setUp()

        self.person_1 = sorted(self.place1.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[0]
        self.person_2 = sorted(self.place2.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[-1]

        self.accepted_position_1 = random.choice(list(places_logic.get_available_positions(center_x=self.person_1.place.x, center_y=self.person_1.place.y)))
        self.accepted_position_2 = random.choice(list(places_logic.get_available_positions(center_x=self.person_2.place.x, center_y=self.person_2.place.y)))

        self.bill_data = bills.building_create.BuildingCreate(person_id=self.person_1.id,
                                                              old_place_name_forms=self.place1.utg_name,
                                                              utg_name=game_names.generator().get_test_name('building-name'),
                                                              x=self.accepted_position_1[0],
                                                              y=self.accepted_position_1[1])
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)
        self.assertEqual(self.bill.data.x, self.accepted_position_1[0])
        self.assertEqual(self.bill.data.y, self.accepted_position_1[1])

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person_1.place)])

    def test_update(self):
        data = linguistics_helpers.get_word_post_data(game_names.generator().get_test_name('new-building-name'), prefix='name')
        data.update({'caption': 'new-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'person': self.person_2.id,
                     'x': self.accepted_position_2[0],
                     'y': self.accepted_position_2[1]})

        form = self.bill.data.get_user_form_update(post=data)
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)
        self.assertEqual(self.bill.data.x, self.accepted_position_2[0])
        self.assertEqual(self.bill.data.y, self.accepted_position_2[1])
        self.assertEqual(self.bill.data.base_name, 'new-building-name-нс,ед,им')

    def check_persons_from_place_in_choices(self, place, persons_ids):
        for person in place.persons:
            if not person.has_building:
                self.assertTrue(person.id in persons_ids)
            else:
                self.assertFalse(person.id in persons_ids)

    def test_user_form_choices(self):

        places_logic.create_building(self.place2.persons[0], utg_name=game_names.generator().get_test_name('r-building-name'))

        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id})

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)

        self.assertTrue(self.bill.data.person_id in persons_ids)

        self.check_persons_from_place_in_choices(self.place1, persons_ids)
        self.check_persons_from_place_in_choices(self.place2, persons_ids)
        self.check_persons_from_place_in_choices(self.place3, persons_ids)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        self.assertEqual(places_models.Building.objects.all().count(), 0)

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('r-building-name')

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertEqual(places_models.Building.objects.all().count(), 1)

        building = places_storage.buildings.all()[0]

        self.assertEqual(building.person.id, self.person_1.id)
        self.assertEqual(building.place.id, self.place1.id)
        self.assertEqual(building.x, self.accepted_position_1[0])
        self.assertEqual(building.y, self.accepted_position_1[1])
        self.assertEqual(building.utg_name, noun)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_duplicate_apply(self):
        self.assertEqual(places_models.Building.objects.all().count(), 0)

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('building-name')

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        dup_noun = game_names.generator().get_test_name('dup-building-name')

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        bill.state = relations.BILL_STATE.VOTING
        bill.save()

        data = bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(dup_noun, prefix='name'))
        data['approved'] = True
        form = bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        # apply first bill
        self.assertTrue(self.bill.apply())

        # apply second bill
        self.assertTrue(bill.apply())

        self.assertEqual(places_models.Building.objects.all().count(), 1)

        building = places_logic.load_building(places_models.Building.objects.all()[0].id)

        self.assertEqual(building.utg_name, noun)
        self.assertNotEqual(building.utg_name, dup_noun)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__duplicate(self):
        self.assertEqual(places_models.Building.objects.all().count(), 0)

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        noun = game_names.generator().get_test_name('building-name')

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        self.assertTrue(self.bill.apply())

        form = bills.building_create.BuildingCreate.ModeratorForm(data)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        bill.state = relations.BILL_STATE.VOTING
        bill.save()

        self.assertFalse(bill.has_meaning())

    def test_has_meaning__wrong_position(self):
        self.bill.data.x = 1000
        self.assertFalse(self.bill.has_meaning())
