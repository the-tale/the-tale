# coding: utf-8

from the_tale.forum.models import Post, Thread, MARKUP_METHOD

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.bills.models import Vote
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRenaming
from the_tale.game.bills.relations import VOTE_TYPE
from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PlaceRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceRenamingTests, self).setUp()

        self.bill = self.create_place_renaming_bill(1)

    def create_place_renaming_bill(self, index):
        self.bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_%d' % index))
        return BillPrototype.create(self.account1, 'bill-%d-caption' % index, 'bill-%d-rationale' % index, self.bill_data)

    def test_create(self):
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(Post.objects.all()[0].markup_method, MARKUP_METHOD.POSTMARKUP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place1)])


    def test_update(self):
        VotePrototype.create(self.account2, self.bill, VOTE_TYPE.FOR)
        VotePrototype.create(self.account3, self.bill, VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account4, self.bill, VOTE_TYPE.REFRAINED)
        self.bill.recalculate_votes()
        self.bill.approved_by_moderator = True
        self.bill.save()

        old_updated_at = self.bill.updated_at

        self.assertEqual(self.bill.votes_for, 2)
        self.assertEqual(self.bill.votes_against, 1)
        self.assertEqual(self.bill.votes_refrained, 1)
        self.assertEqual(Vote.objects.all().count(), 4)
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.base_name, u'new_name_1-нс,ед,им')
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(Post.objects.all().count(), 1)

        new_name = names.generator.get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'new-caption',
                     'rationale': 'new-rationale',
                     'place': self.place2.id})

        form = PlaceRenaming.UserForm(data)

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertTrue(old_updated_at < self.bill.updated_at)
        self.assertTrue(self.bill.state.is_VOTING)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(self.bill.votes_refrained, 0)
        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertEqual(self.bill.caption, 'new-caption')
        self.assertEqual(self.bill.rationale, 'new-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.data.base_name, u'new-new-name-нс,ед,им')
        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertEqual(Thread.objects.get(id=self.bill.forum_thread_id).caption, 'new-caption')

    def test_update_by_moderator(self):

        self.assertEqual(self.bill.approved_by_moderator, False)


        noun = names.generator.get_test_name('new-name')
        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'approved': True})

        form = PlaceRenaming.ModeratorForm(data)

        self.assertTrue(form.is_valid())

        self.bill.update_by_moderator(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(self.bill.state.is_VOTING)
        self.assertEqual(self.bill.approved_by_moderator, True)

        self.assertEqual(self.bill.data.name_forms.forms, noun.forms)

    def test_remove(self):
        thread = Thread.objects.get(id=self.bill.forum_thread_id)
        self.bill.remove(self.account1)
        self.assertTrue(self.bill.state.is_REMOVED)
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertNotEqual(Thread.objects.get(id=self.bill.forum_thread_id).caption, thread.caption)

    def test_get_minimum_created_time_of_active_bills(self):
        self.assertEqual(self.bill.created_at, BillPrototype.get_minimum_created_time_of_active_bills())

        self.bill.remove(initiator=self.account1)

        # not there are no anothe bills an get_minimum_created_time_of_active_bills return now()
        self.assertTrue(self.bill.created_at < BillPrototype.get_minimum_created_time_of_active_bills())
