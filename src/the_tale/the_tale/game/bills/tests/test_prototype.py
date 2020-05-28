
import smart_imports

smart_imports.all()


class BillPrototypeTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(BillPrototypeTests, self).setUp()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)

        game_tt_services.debug_clear_service()

    def create_bill(self, account=None, depends_on_id=None):
        if account is None:
            account = self.account1
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        return prototypes.BillPrototype.create(account,
                                               'bill-1-caption',
                                               bill_data,
                                               chronicle_on_accepted='chronicle-on-accepted',
                                               depends_on_id=depends_on_id)

    def test_accepted_bills_count(self):
        for state in relations.BILL_STATE.records:
            bill = self.create_bill(self.account1)
            bill.state = state
            bill.save()

        for state in relations.BILL_STATE.records:
            bill = self.create_bill(self.account2)
            bill.state = state
            bill.save()

        self.assertEqual(prototypes.BillPrototype.accepted_bills_count(self.account1.id), 1)
        self.assertEqual(prototypes.BillPrototype.accepted_bills_count(self.account2.id), 1)
        self.assertEqual(prototypes.BillPrototype.accepted_bills_count(self.account3.id), 0)

    def test_is_active_bills_limit_reached__free_accounts(self):
        for i in range(c.FREE_ACCOUNT_MAX_ACTIVE_BILLS):
            self.assertFalse(prototypes.BillPrototype.is_active_bills_limit_reached(self.account1))
            self.create_bill()

        self.assertTrue(prototypes.BillPrototype.is_active_bills_limit_reached(self.account1))

    def test_is_active_bills_limit_reached__premiun_accounts(self):
        self.account1.prolong_premium(30)
        self.account1.save()

        for i in range(c.PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS):
            self.assertFalse(prototypes.BillPrototype.is_active_bills_limit_reached(self.account1))
            self.create_bill()

        self.assertTrue(prototypes.BillPrototype.is_active_bills_limit_reached(self.account1))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_vote__places_restrictions__no_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', []):
            self.assertTrue(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_vote__places_restrictions__no_allowed_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertFalse(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.places.objects.Place.is_new', True)
    def test_can_vote__places_restrictions__no_allowed_places__with_timeout(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertTrue(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_vote__places_restrictions__allowed_place(self):
        bill = self.create_bill()

        places_logic.add_fame(self.hero.id, fames=[(self.place2.id, c.BILLS_FAME_BORDER)])

        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertTrue(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_vote__places_restrictions__fame_border(self):
        bill = self.create_bill()

        places_logic.add_fame(self.hero.id, fames=[(self.place2.id, c.BILLS_FAME_BORDER-1)])

        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertFalse(bill.can_vote(self.hero))

    def test_remove_duplicate_actors(self):
        bill = self.create_bill()

        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place1, self.place3]):
            self.assertEqual(bill.actors, [self.place1, self.place3])

    def test_is_delayed__no_dependencies(self):
        bill = self.create_bill()
        self.assertFalse(bill.is_delayed)

    def test_is_delayed__has_dependencies(self):
        base_bill = self.create_bill()
        child_bill = self.create_bill(depends_on_id=base_bill.id)

        self.assertTrue(child_bill.is_delayed)

    def test_has_meaning_with_dependency_state(self):
        base_bill = self.create_bill()
        child_bill = self.create_bill(depends_on_id=base_bill.id)

        for state in relations.BILL_STATE.records:
            base_bill.state = state
            base_bill.save()

            child_bill.reload()

            self.assertEqual(not state.break_dependent_bills, child_bill.has_meaning())


class TestPrototypeApply(helpers.BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeApply, self).setUp()

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def check_place(self, place_id, name, name_forms):
        self.assertEqual(places_storage.places[place_id].name, name)
        self.assertEqual(places_storage.places[place_id].utg_name.forms, name_forms)

    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(exceptions.ApplyBillInWrongStateError, self.bill.apply)

        places_storage.places.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_not_approved(self):
        self.bill.approved_by_moderator = False
        self.bill.save()

        self.assertRaises(exceptions.ApplyUnapprovedBillError, self.bill.apply)

        places_storage.places.sync(force=True)

        self.assertEqual(self.bill.applyed_at_turn, None)

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    def test_wrong_time(self):
        self.assertRaises(exceptions.ApplyBillBeforeVoteWasEndedError, self.bill.apply)
        places_storage.places.sync(force=True)
        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.51)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_not_enough_voices_percents(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        game_turn.increment()
        game_turn.increment()

        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(forum_models.Post.objects.all().count(), 1)

        with self.check_not_changed(lambda: self.place1.attrs.stability):
            with self.check_not_changed(lambda: accounts_prototypes.AccountPrototype.get_by_id(self.bill.owner.id).actual_bills):
                with self.check_not_changed(lambda: self.bill.owner.actual_bills):
                    self.assertFalse(self.bill.apply())

            self.assertTrue(self.bill.state.is_REJECTED)

            self.assertEqual(forum_models.Post.objects.all().count(), 2)

            bill = prototypes.BillPrototype.get_by_id(self.bill.id)
            self.assertTrue(bill.state.is_REJECTED)

            places_storage.places.sync(force=True)

            self.place1.refresh_attributes()

        self.assertEqual(bill.applyed_at_turn, game_turn.number())

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

        page, total_records, events = chronicle_tt_services.chronicle.cmd_get_events(tags=(), page=1, records_on_page=100)

        self.assertEqual(total_records, 0)

    def prepair_data_to_approve(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)
        prototypes.VotePrototype.create(self.account4, self.bill, relations.VOTE_TYPE.REFRAINED)

        ##################################
        # set name forms

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(self.bill.data.name_forms, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_approved(self):
        game_turn.increment()
        game_turn.increment()
        game_turn.increment()

        self.prepair_data_to_approve()

        self.assertEqual(forum_models.Post.objects.all().count(), 1)

        self.assertTrue(self.bill.apply())

        self.assertEqual(accounts_prototypes.AccountPrototype.get_by_id(self.bill.owner.id).actual_bills,
                         [utils_logic.to_timestamp(self.bill.voting_end_at)])

        self.assertEqual(self.bill.owner.actual_bills,
                         [utils_logic.to_timestamp(self.bill.voting_end_at)])

        self.assertTrue(self.bill.state.is_ACCEPTED)

        self.assertEqual(forum_models.Post.objects.all().count(), 2)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        places_storage.places.sync(force=True)

        self.place1.refresh_attributes()
        self.assertTrue(self.place1.attrs.stability < 1.0)

        self.assertEqual(bill.applyed_at_turn, game_turn.number())

        self.check_place(self.place1.id, 'new_name_1-нс,ед,им', self.bill.data.name_forms.forms)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_achievements(self):
        self.prepair_data_to_approve()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.assertTrue(self.bill.apply())

        self.assertEqual(verify_achievements.call_args_list,
                         [mock.call(account_id=self.account1.id,
                                    type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_ACCEPTED_BILLS,
                                    old_value=0,
                                    new_value=1)])

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_chronicle(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        self.prepair_data_to_approve()

        self.assertTrue(self.bill.apply())

        page, total_records, events = chronicle_tt_services.chronicle.cmd_get_events(tags=(), page=1, records_on_page=100)

        self.assertEqual(total_records, 1)

        self.assertEqual(events[0].message, self.bill.chronicle_on_accepted)


class TestPrototypeStop(helpers.BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeStop, self).setUp()

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(exceptions.StopBillInWrongStateError, self.bill.stop)

    def test_stopped(self):
        with self.check_delta(forum_models.Post.objects.all().count, 1):
            self.bill.stop()

        self.assertTrue(self.bill.state.is_STOPPED)


class TestPrototypeEnd(helpers.BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeEnd, self).setUp()

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.state = relations.BILL_STATE.ACCEPTED

        game_turn.increment()

    def test_not_accepted(self):
        for state in relations.BILL_STATE.records:
            if state.is_ACCEPTED:
                continue
            self.bill.state = state

            with mock.patch('the_tale.game.bills.bills.base_bill.BaseBill.end') as end:
                self.assertRaises(exceptions.EndBillInWrongStateError, self.bill.end)

            self.assertEqual(end.call_count, 0)

    def test_already_ended(self):
        self.bill._model.ended_at = datetime.datetime.now()

        with mock.patch('the_tale.game.bills.bills.base_bill.BaseBill.end') as end:
            self.assertRaises(exceptions.EndBillAlreadyEndedError, self.bill.end)

        self.assertEqual(end.call_count, 0)

    def test_success(self):
        with mock.patch('the_tale.game.bills.bills.base_bill.BaseBill.end') as end:
            self.bill.end()

        self.assertEqual(end.call_count, 1)


class GetApplicableBillsTest(helpers.BaseTestPrototypes):

    def setUp(self):
        super(GetApplicableBillsTest, self).setUp()

        self.bill_data = bills.place_description.PlaceDescripton(place_id=self.place1.id, description='description')
        self.bill_1 = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')
        self.bill_2 = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')
        self.bill_3 = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        prototypes.BillPrototype._model_class.objects.all().update(updated_at=datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.BILL_LIVE_TIME),
                                                                   approved_by_moderator=True)

        self.bill_1.reload()
        self.bill_2.reload()
        self.bill_3.reload()

    def test_all(self):
        self.assertEqual(set(prototypes.BillPrototype.get_applicable_bills_ids()),
                         set((self.bill_1.id, self.bill_2.id, self.bill_3.id)))

    def test_wrong_state(self):

        for state in relations.BILL_STATE.records:
            if state.is_VOTING:
                continue
            self.bill_1.state = state
            self.bill_1.save()
            self.assertEqual(set(prototypes.BillPrototype.get_applicable_bills_ids()), set((self.bill_2.id, self.bill_3.id)))

    def test_approved_by_moderator(self):

        self.bill_2.approved_by_moderator = False
        self.bill_2.save()
        self.assertEqual(set(prototypes.BillPrototype.get_applicable_bills_ids()), set((self.bill_1.id, self.bill_3.id)))

    def test_voting_not_ended(self):

        self.bill_3._model.updated_at = datetime.datetime.now()
        self.bill_3.save()
        self.assertEqual(set(prototypes.BillPrototype.get_applicable_bills_ids()), set((self.bill_1.id, self.bill_2.id)))


class TestActorPrototype(helpers.BaseTestPrototypes):

    def setUp(self):
        super(TestActorPrototype, self).setUp()

        self.bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_actors_created(self):
        self.assertTrue(models.Actor.objects.all().exists())

    def test_actors_after_user_update(self):
        old_actors_timestamps = list(models.Actor.objects.all().values_list('created_at', flat=True))

        noun = game_names.generator().get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'caption': 'new-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'place': self.place2.id})

        form = bills.place_renaming.PlaceRenaming.UserForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update(form)

        new_actors_timestamps = list(models.Actor.objects.all().values_list('created_at', flat=True))

        self.assertFalse(set(old_actors_timestamps) & set(new_actors_timestamps))
        self.assertTrue(new_actors_timestamps)


class TestVotePrototype(helpers.BaseTestPrototypes):

    def setUp(self):
        super(TestVotePrototype, self).setUp()

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def test_votes_count(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(prototypes.VotePrototype.votes_count(self.account1.id), 1)
        self.assertEqual(prototypes.VotePrototype.votes_count(self.account2.id), 1)
        self.assertEqual(prototypes.VotePrototype.votes_count(self.account3.id), 1)
        self.assertEqual(prototypes.VotePrototype.votes_count(self.account4.id), 0)

    def test_votes_for_count(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(prototypes.VotePrototype.votes_for_count(self.account1.id), 1)
        self.assertEqual(prototypes.VotePrototype.votes_for_count(self.account2.id), 0)
        self.assertEqual(prototypes.VotePrototype.votes_for_count(self.account3.id), 0)
        self.assertEqual(prototypes.VotePrototype.votes_for_count(self.account4.id), 0)

    def test_votes_agains_count(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(prototypes.VotePrototype.votes_against_count(self.account1.id), 0)
        self.assertEqual(prototypes.VotePrototype.votes_against_count(self.account2.id), 1)
        self.assertEqual(prototypes.VotePrototype.votes_against_count(self.account3.id), 0)
        self.assertEqual(prototypes.VotePrototype.votes_against_count(self.account4.id), 0)

    def test_vote_for_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.FOR)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=0)])

    def test_vote_agains_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=0),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=1)])

    def test_vote_refrained_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=0),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=0)])
