# coding: utf-8
import mock
import datetime

from dext.utils import s11n

from textgen.words import Noun

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.forum.models import Post

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.bills.models import Actor
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE,BILL_DURATION
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRenaming, PlaceDescripton
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import exceptions

from the_tale.game.map.places.storage import places_storage


class BaseTestPrototypes(TestCase):

    NAME_FORMS = (u'new_name_1',
                  u'new_name_2',
                  u'new_name_3',
                  u'new_name_4',
                  u'new_name_5',
                  u'new_name_6',
                  u'new_name_7',
                  u'new_name_8',
                  u'new_name_9',
                  u'new_name_10',
                  u'new_name_11',
                  u'new_name_12')


    def setUp(self):
        super(BaseTestPrototypes, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4', 'test_user4@test.com', '111111')
        self.account4 = AccountPrototype.get_by_id(account_id)

        from the_tale.forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)


class BillPrototypeTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPrototypeTests, self).setUp()

        self.hero = HeroPrototype.get_by_account_id(self.account2.id)


    def create_bill(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        return BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

    def test_is_active_bills_limit_reached(self):
        self.assertFalse(BillPrototype.is_active_bills_limit_reached(self.account1))

        self.create_bill()

        self.assertTrue(BillPrototype.is_active_bills_limit_reached(self.account1))

    def test_can_vote__places_restrictions__no_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', []):
            self.assertTrue(bill.can_vote(self.hero))

    def test_can_vote__places_restrictions__no_allowed_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertFalse(bill.can_vote(self.hero))

    def test_can_vote__places_restrictions__allowed_place(self):
        bill = self.create_bill()

        self.hero.places_history.add_place(self.place2.id)

        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertTrue(bill.can_vote(self.hero))



class TestPrototypeApply(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeApply, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.bill.approved_by_moderator = True
        self.bill.save()

    def check_place(self, place_id, name, name_forms):
        self.assertEqual(places_storage[place_id].name, name)
        self.assertEqual(places_storage[place_id].normalized_name.forms, name_forms)


    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(exceptions.ApplyBillInWrongStateError, self.bill.apply)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name.forms)

    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_not_approved(self):
        self.bill.approved_by_moderator = False
        self.bill.save()

        self.assertRaises(exceptions.ApplyUnapprovedBillError, self.bill.apply)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name.forms)

    def test_wrong_time(self):
        self.assertRaises(exceptions.ApplyUnapprovedBillError, self.bill.apply)
        places_storage.sync(force=True)
        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name.forms)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.51)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_not_enough_voices_percents(self):
        VotePrototype.create(self.account2, self.bill, VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, VOTE_TYPE.REFRAINED)

        self.assertEqual(Post.objects.all().count(), 1)

        self.assertFalse(self.bill.apply())
        self.assertTrue(self.bill.state._is_REJECTED)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_REJECTED)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name.forms)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_approved(self):
        VotePrototype.create(self.account2, self.bill, VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, VOTE_TYPE.FOR)
        VotePrototype.create(self.account4, self.bill, VOTE_TYPE.REFRAINED)

        ##################################
        # set name forms
        noun = Noun(normalized=self.bill.data.base_name.lower(),
                    forms=self.NAME_FORMS,
                    properties=(u'мр',))

        form = PlaceRenaming.ModeratorForm({'approved': True,
                                            'name_forms': s11n.to_json(noun.serialize()) })

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

        self.assertEqual(Post.objects.all().count(), 1)

        self.assertTrue(self.bill.apply())
        self.assertTrue(self.bill.state._is_ACCEPTED)
        self.assertEqual(self.bill.ends_at_turn, None)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_ACCEPTED)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, 'new_name_1', self.NAME_FORMS)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_approved__duration(self):

        ##################################
        # set name forms
        noun = Noun(normalized=self.bill.data.base_name.lower(),
                    forms=self.NAME_FORMS,
                    properties=(u'мр',))

        form = PlaceRenaming.ModeratorForm({'approved': True,
                                            'name_forms': s11n.to_json(noun.serialize()) })

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

        self.assertEqual(Post.objects.all().count(), 1)

        self.bill._model.duration = BILL_DURATION.YEAR
        self.bill.save()

        self.assertTrue(self.bill.apply())
        self.assertTrue(self.bill.state._is_ACCEPTED)
        self.assertEqual(self.bill.ends_at_turn, TimePrototype.get_current_turn_number() + BILL_DURATION.YEAR.game_months * c.TURNS_IN_GAME_MONTH)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_ACCEPTED)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, 'new_name_1', self.NAME_FORMS)


class TestPrototypeEnd(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeEnd, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.bill.state = BILL_STATE.ACCEPTED
        self.bill._model.ends_at_turn = 0

        TimePrototype.get_current_time().increment_turn()

    def test_not_accepted(self):
        for state in BILL_STATE._records:
            if state._is_ACCEPTED:
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

    def test_before_timeout(self):
        self.bill._model.ends_at_turn = TimePrototype.get_current_turn_number() + 1

        with mock.patch('the_tale.game.bills.bills.base_bill.BaseBill.end') as end:
            self.assertRaises(exceptions.EndBillBeforeTimeError, self.bill.end)

        self.assertEqual(end.call_count, 0)

    def test_success(self):
        with mock.patch('the_tale.game.bills.bills.base_bill.BaseBill.end') as end:
            self.bill.end()

        self.assertEqual(end.call_count, 1)



class GetApplicableBillsTest(BaseTestPrototypes):

    def setUp(self):
        super(GetApplicableBillsTest, self).setUp()

        self.bill_data = PlaceDescripton(place_id=self.place1.id, description='description')
        self.bill_1 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)
        self.bill_2 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)
        self.bill_3 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)

        BillPrototype._model_class.objects.all().update(updated_at=datetime.datetime.now() - datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME),
                                                        approved_by_moderator=True)

        self.bill_1.reload()
        self.bill_2.reload()
        self.bill_3.reload()

    def test_all(self):
        self.assertEqual(set(bill.id for bill in BillPrototype.get_applicable_bills()),
                         set((self.bill_1.id, self.bill_2.id, self.bill_3.id)))

    def test_wrong_state(self):

        for state in BILL_STATE._records:
            if state._is_VOTING:
                continue
            self.bill_1.state = state
            self.bill_1.save()
            self.assertEqual(set(bill.id for bill in BillPrototype.get_applicable_bills()), set((self.bill_2.id, self.bill_3.id)))

    def test_approved_by_moderator(self):

        self.bill_2.approved_by_moderator = False
        self.bill_2.save()
        self.assertEqual(set(bill.id for bill in BillPrototype.get_applicable_bills()), set((self.bill_1.id, self.bill_3.id)))

    def test_voting_not_ended(self):

        self.bill_3._model.updated_at = datetime.datetime.now()
        self.bill_3.save()
        self.assertEqual(set(bill.id for bill in BillPrototype.get_applicable_bills()), set((self.bill_1.id, self.bill_2.id)))


class GetBillsToEndTest(BaseTestPrototypes):

    def setUp(self):
        super(GetBillsToEndTest, self).setUp()

        self.bill_data = PlaceDescripton(place_id=self.place1.id, description='description')
        self.bill_1 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)
        self.bill_2 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)
        self.bill_3 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)

        BillPrototype._model_class.objects.all().update(ends_at_turn=0,
                                                        state=BILL_STATE.ACCEPTED,
                                                        approved_by_moderator=True)

        TimePrototype.get_current_time().increment_turn()

        self.bill_1.reload()
        self.bill_2.reload()
        self.bill_3.reload()

    def test_all(self):
        self.assertEqual(set(bill.id for bill in BillPrototype.get_bills_to_end()),
                         set((self.bill_1.id, self.bill_2.id, self.bill_3.id)))

    def test_wrong_state(self):

        for state in BILL_STATE._records:
            if state._is_ACCEPTED:
                continue
            self.bill_1.state = state
            self.bill_1.save()
            self.assertEqual(set(bill.id for bill in BillPrototype.get_bills_to_end()), set((self.bill_2.id, self.bill_3.id)))

    def test_already_ended(self):

        self.bill_2._model.ended_at = datetime.datetime.now()
        self.bill_2.save()
        self.assertEqual(set(bill.id for bill in BillPrototype.get_bills_to_end()), set((self.bill_1.id, self.bill_3.id)))

    def test_not_ended(self):

        self.bill_3._model.ends_at_turn = TimePrototype.get_current_turn_number() + 1
        self.bill_3.save()
        self.assertEqual(set(bill.id for bill in BillPrototype.get_bills_to_end()), set((self.bill_1.id, self.bill_2.id)))



class TestActorPrototype(BaseTestPrototypes):

    def setUp(self):
        super(TestActorPrototype, self).setUp()

        self.bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)

    def test_actors_created(self):
        self.assertTrue(Actor.objects.all().exists())

    def test_actors_after_user_update(self):
        old_actors_timestamps = list(Actor.objects.all().values_list('created_at', flat=True))

        form = PlaceRenaming.UserForm({'caption': 'new-caption',
                                       'rationale': 'new-rationale',
                                       'place': self.place2.id,
                                       'new_name': 'new-new-name'})

        self.assertTrue(form.is_valid())
        self.bill.update(form)

        new_actors_timestamps = list(Actor.objects.all().values_list('created_at', flat=True))

        self.assertFalse(set(old_actors_timestamps) & set(new_actors_timestamps))
        self.assertTrue(new_actors_timestamps)
