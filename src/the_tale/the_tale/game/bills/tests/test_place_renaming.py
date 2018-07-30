
import smart_imports

smart_imports.all()


class PlaceRenamingTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PlaceRenamingTests, self).setUp()

        self.bill = self.create_place_renaming_bill(1)

    def create_place_renaming_bill(self, index):
        self.bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_%d' % index))
        return prototypes.BillPrototype.create(self.account1, 'bill-%d-caption' % index, self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.chronicle_on_accepted, 'chronicle-on-accepted')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(forum_models.Post.objects.all().count(), 1)
        self.assertEqual(forum_models.Post.objects.all()[0].markup_method, forum_relations.MARKUP_METHOD.POSTMARKUP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place1)])

    def test_update(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.FOR)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account4, self.bill, relations.VOTE_TYPE.REFRAINED)
        self.bill.recalculate_votes()
        self.bill.approved_by_moderator = True
        self.bill.save()

        old_updated_at = self.bill.updated_at

        self.assertEqual(self.bill.votes_for, 2)
        self.assertEqual(self.bill.votes_against, 1)
        self.assertEqual(self.bill.votes_refrained, 1)
        self.assertEqual(models.Vote.objects.all().count(), 4)
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.base_name, 'new_name_1-нс,ед,им')
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(forum_models.Post.objects.all().count(), 1)

        new_name = game_names.generator().get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'new-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'place': self.place2.id})

        form = bills.place_renaming.PlaceRenaming.UserForm(data)

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertTrue(old_updated_at < self.bill.updated_at)
        self.assertTrue(self.bill.state.is_VOTING)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(self.bill.votes_refrained, 0)
        self.assertEqual(models.Vote.objects.all().count(), 1)
        self.assertEqual(self.bill.caption, 'new-caption')
        self.assertEqual(self.bill.chronicle_on_accepted, 'chronicle-on-accepted-2')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.data.base_name, 'new-new-name-нс,ед,им')
        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(forum_models.Post.objects.all().count(), 2)
        self.assertEqual(forum_models.Thread.objects.get(id=self.bill.forum_thread_id).caption, 'new-caption')

    def test_update_by_moderator(self):

        self.assertEqual(self.bill.approved_by_moderator, False)

        noun = game_names.generator().get_test_name('new-name')

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(noun, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())

        self.bill.update_by_moderator(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(self.bill.state.is_VOTING)
        self.assertEqual(self.bill.approved_by_moderator, True)

        self.assertEqual(self.bill.data.name_forms.forms, noun.forms)

    def test_remove(self):
        thread = forum_models.Thread.objects.get(id=self.bill.forum_thread_id)
        self.bill.remove(self.account1)
        self.assertTrue(self.bill.state.is_REMOVED)
        self.assertEqual(forum_models.Post.objects.all().count(), 2)
        self.assertNotEqual(forum_models.Thread.objects.get(id=self.bill.forum_thread_id).caption, thread.caption)

    def test_get_minimum_created_time_of_active_bills(self):
        self.assertEqual(self.bill.created_at, prototypes.BillPrototype.get_minimum_created_time_of_active_bills())

        self.bill.remove(initiator=self.account1)

        # not there are no anothe bills an get_minimum_created_time_of_active_bills return now()
        self.assertTrue(self.bill.created_at < prototypes.BillPrototype.get_minimum_created_time_of_active_bills())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        new_name = game_names.generator().get_test_name('new-new-name')

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(new_name, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertEqual(self.bill.data.place.utg_name, new_name)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__duplicate_name(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        new_name = game_names.generator().get_test_name('new-new-name')
        self.bill.data.place.set_utg_name(new_name)

        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(new_name, prefix='name'))
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertFalse(self.bill.has_meaning())
