# coding: utf-8

from dext.utils import s11n

from textgen.words import Noun

from forum.models import Post, Thread, MARKUP_METHOD

from game.bills.models import Vote
from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PlaceRenaming
from game.bills.tests.prototype_tests import BaseTestPrototypes


class PlaceRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceRenamingTests, self).setUp()

        self.bill = self.create_place_renaming_bill(1)

    def create_place_renaming_bill(self, index):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_%d' % index)
        return BillPrototype.create(self.account1, 'bill-%d-caption' % index, 'bill-%d-rationale' % index, bill_data)

    def test_create(self):
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(Post.objects.all()[0].markup_method, MARKUP_METHOD.POSTMARKUP)


    def test_update(self):
        VotePrototype.create(self.account2, self.bill, True)
        VotePrototype.create(self.account3, self.bill, False)
        self.bill.recalculate_votes()
        self.bill.approved_by_moderator = True
        self.bill.save()

        old_updated_at = self.bill.updated_at

        self.assertEqual(self.bill.votes_for, 2)
        self.assertEqual(self.bill.votes_against, 1)
        self.assertEqual(Vote.objects.all().count(), 3)
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.base_name, 'new_name_1')
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(Post.objects.all().count(), 1)

        form = PlaceRenaming.UserForm({'caption': 'new-caption',
                                       'rationale': 'new-rationale',
                                       'place': self.place2.id,
                                       'new_name': 'new-new-name'})

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertTrue(old_updated_at < self.bill.updated_at)
        self.assertTrue(self.bill.state._is_VOTING)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertEqual(self.bill.caption, 'new-caption')
        self.assertEqual(self.bill.rationale, 'new-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.data.base_name, 'new-new-name')
        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertEqual(Thread.objects.get(id=self.bill.forum_thread_id).caption, 'new-caption')

    def test_update_by_moderator(self):

        self.assertEqual(self.bill.approved_by_moderator, False)

        self.assertEqual(self.bill.data.name_forms.forms, tuple([u'new_name_1']*12))

        noun = Noun(normalized=self.bill.data.base_name.lower(),
                    forms=self.NAME_FORMS,
                    properties=(u'мр',))

        form = PlaceRenaming.ModeratorForm({'approved': True,
                                            'name_forms': s11n.to_json(noun.serialize()) })

        self.assertTrue(form.is_valid())

        self.bill.update_by_moderator(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(self.bill.state._is_VOTING)
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.name_forms.forms, self.NAME_FORMS)

    def test_remove(self):
        thread = Thread.objects.get(id=self.bill.forum_thread_id)
        self.bill.remove(self.account1)
        self.assertTrue(self.bill.state._is_REMOVED)
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertNotEqual(Thread.objects.get(id=self.bill.forum_thread_id).caption, thread.caption)

    def test_get_minimum_created_time_of_active_bills(self):
        self.assertEqual(self.bill.created_at, BillPrototype.get_minimum_created_time_of_active_bills())

        self.bill.remove(initiator=self.account1)

        # not there are no anothe bills an get_minimum_created_time_of_active_bills return now()
        self.assertTrue(self.bill.created_at < BillPrototype.get_minimum_created_time_of_active_bills())
