# coding: utf-8
import mock
import datetime

from the_tale.forum.models import Post

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.game.heroes import logic as heroes_logic


from the_tale.game.bills.models import Actor
from the_tale.game.bills import relations
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRenaming, PlaceDescripton
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import exceptions
from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.map.places.storage import places_storage


class BillPrototypeTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPrototypeTests, self).setUp()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)


    def create_bill(self, account=None):
        if account is None:
            account = self.account1
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        return BillPrototype.create(account, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_accepted_bills_count(self):
        for state in relations.BILL_STATE.records:
            bill = self.create_bill(self.account1)
            bill.state = state
            bill.save()

        for state in relations.BILL_STATE.records:
            bill = self.create_bill(self.account2)
            bill.state = state
            bill.save()

        self.assertEqual(BillPrototype.accepted_bills_count(self.account1.id), 1)
        self.assertEqual(BillPrototype.accepted_bills_count(self.account2.id), 1)
        self.assertEqual(BillPrototype.accepted_bills_count(self.account3.id), 0)


    def test_is_active_bills_limit_reached(self):
        self.assertFalse(BillPrototype.is_active_bills_limit_reached(self.account1))

        self.create_bill()

        self.assertTrue(BillPrototype.is_active_bills_limit_reached(self.account1))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_vote__places_restrictions__no_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', []):
            self.assertTrue(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_vote__places_restrictions__no_allowed_places(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertFalse(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', True)
    def test_can_vote__places_restrictions__no_allowed_places__with_timeout(self):
        bill = self.create_bill()
        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertTrue(bill.can_vote(self.hero))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_vote__places_restrictions__allowed_place(self):
        bill = self.create_bill()

        self.hero.places_history.add_place(self.place2.id)

        with mock.patch('the_tale.game.bills.bills.place_renaming.PlaceRenaming.actors', [self.place1, self.place2, self.place3]):
            self.assertTrue(bill.can_vote(self.hero))



class TestPrototypeApply(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeApply, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def check_place(self, place_id, name, name_forms):
        self.assertEqual(places_storage[place_id].name, name)
        self.assertEqual(places_storage[place_id].utg_name.forms, name_forms)


    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(exceptions.ApplyBillInWrongStateError, self.bill.apply)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', lambda x: datetime.timedelta(seconds=0))
    def test_not_approved(self):
        self.bill.approved_by_moderator = False
        self.bill.save()

        self.assertRaises(exceptions.ApplyUnapprovedBillError, self.bill.apply)

        places_storage.sync(force=True)

        self.assertEqual(self.bill.applyed_at_turn, None)

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    def test_wrong_time(self):
        self.assertRaises(exceptions.ApplyBillBeforeVoteWasEndedError, self.bill.apply)
        places_storage.sync(force=True)
        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.51)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_not_enough_voices_percents(self):

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        current_time.increment_turn()

        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(Post.objects.all().count(), 1)

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
            self.assertFalse(self.bill.apply())

        self.assertEqual(cmd_run_account_method.call_count, 0)
        self.assertTrue(self.bill.state.is_REJECTED)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_REJECTED)

        places_storage.sync(force=True)

        self.place1.sync_parameters()
        self.assertEqual(self.place1.stability, 1.0)

        self.assertEqual(bill.applyed_at_turn, current_time.turn_number)

        self.check_place(self.place1.id, self.place1.name, self.place1.utg_name.forms)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_approved(self):
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        current_time.increment_turn()
        current_time.increment_turn()

        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)
        VotePrototype.create(self.account4, self.bill, relations.VOTE_TYPE.REFRAINED)

        ##################################
        # set name forms
        data = linguistics_helpers.get_word_post_data(self.bill.data.name_forms, prefix='name')
        data.update({'approved': True})
        form = PlaceRenaming.ModeratorForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

        self.assertEqual(Post.objects.all().count(), 1)

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
            self.assertTrue(self.bill.apply())

        self.assertEqual(cmd_run_account_method.call_args_list, [mock.call(account_id=self.bill.owner.id,
                                                                           method_name=accounts_prototypes.AccountPrototype.update_actual_bills.__name__,
                                                                           data={})])

        self.assertTrue(self.bill.state.is_ACCEPTED)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        places_storage.sync(force=True)

        self.place1.sync_parameters()
        self.assertTrue(self.place1.stability < 1.0)

        self.assertEqual(bill.applyed_at_turn, current_time.turn_number)

        self.check_place(self.place1.id, u'new_name_1-нс,ед,им', self.bill.data.name_forms.forms)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_achievements(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)
        VotePrototype.create(self.account4, self.bill, relations.VOTE_TYPE.REFRAINED)

        ##################################
        # set name forms
        data = linguistics_helpers.get_word_post_data(self.bill.data.name_forms, prefix='name')
        data.update({'approved': True})
        form = PlaceRenaming.ModeratorForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.assertTrue(self.bill.apply())

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account1.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_ACCEPTED_BILLS,
                                                                        old_value=0,
                                                                        new_value=1)])


class TestPrototypeStop(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeStop, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(exceptions.StopBillInWrongStateError, self.bill.stop)

    def test_stopped(self):
        with self.check_delta(Post.objects.all().count, 1):
            self.bill.stop()

        self.assertTrue(self.bill.state.is_STOPPED)



class TestPrototypeEnd(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeEnd, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.state = relations.BILL_STATE.ACCEPTED

        TimePrototype.get_current_time().increment_turn()

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




class GetApplicableBillsTest(BaseTestPrototypes):

    def setUp(self):
        super(GetApplicableBillsTest, self).setUp()

        self.bill_data = PlaceDescripton(place_id=self.place1.id, description='description')
        self.bill_1 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')
        self.bill_2 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')
        self.bill_3 = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        BillPrototype._model_class.objects.all().update(updated_at=datetime.datetime.now() - datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME),
                                                        approved_by_moderator=True)

        self.bill_1.reload()
        self.bill_2.reload()
        self.bill_3.reload()

    def test_all(self):
        self.assertEqual(set(BillPrototype.get_applicable_bills_ids()),
                         set((self.bill_1.id, self.bill_2.id, self.bill_3.id)))

    def test_wrong_state(self):

        for state in relations.BILL_STATE.records:
            if state.is_VOTING:
                continue
            self.bill_1.state = state
            self.bill_1.save()
            self.assertEqual(set(BillPrototype.get_applicable_bills_ids()), set((self.bill_2.id, self.bill_3.id)))

    def test_approved_by_moderator(self):

        self.bill_2.approved_by_moderator = False
        self.bill_2.save()
        self.assertEqual(set(BillPrototype.get_applicable_bills_ids()), set((self.bill_1.id, self.bill_3.id)))

    def test_voting_not_ended(self):

        self.bill_3._model.updated_at = datetime.datetime.now()
        self.bill_3.save()
        self.assertEqual(set(BillPrototype.get_applicable_bills_ids()), set((self.bill_1.id, self.bill_2.id)))



class TestActorPrototype(BaseTestPrototypes):

    def setUp(self):
        super(TestActorPrototype, self).setUp()

        self.bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_actors_created(self):
        self.assertTrue(Actor.objects.all().exists())

    def test_actors_after_user_update(self):
        old_actors_timestamps = list(Actor.objects.all().values_list('created_at', flat=True))

        noun = names.generator.get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'caption': 'new-caption',
                     'rationale': 'new-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'place': self.place2.id})

        form = PlaceRenaming.UserForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update(form)

        new_actors_timestamps = list(Actor.objects.all().values_list('created_at', flat=True))

        self.assertFalse(set(old_actors_timestamps) & set(new_actors_timestamps))
        self.assertTrue(new_actors_timestamps)


class TestVotePrototype(BaseTestPrototypes):

    def setUp(self):
        super(TestVotePrototype, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.approved_by_moderator = True
        self.bill.save()

    def test_votes_count(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(VotePrototype.votes_count(self.account1.id), 1)
        self.assertEqual(VotePrototype.votes_count(self.account2.id), 1)
        self.assertEqual(VotePrototype.votes_count(self.account3.id), 1)
        self.assertEqual(VotePrototype.votes_count(self.account4.id), 0)

    def test_votes_for_count(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(VotePrototype.votes_for_count(self.account1.id), 1)
        self.assertEqual(VotePrototype.votes_for_count(self.account2.id), 0)
        self.assertEqual(VotePrototype.votes_for_count(self.account3.id), 0)
        self.assertEqual(VotePrototype.votes_for_count(self.account4.id), 0)

    def test_votes_agains_count(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(VotePrototype.votes_against_count(self.account1.id), 0)
        self.assertEqual(VotePrototype.votes_against_count(self.account2.id), 1)
        self.assertEqual(VotePrototype.votes_against_count(self.account3.id), 0)
        self.assertEqual(VotePrototype.votes_against_count(self.account4.id), 0)



    def test_vote_for_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.FOR)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=0)])

    def test_vote_agains_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=0),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=1)])


    def test_vote_refrained_achievements(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.REFRAINED)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL,
                                                                        old_value=0,
                                                                        new_value=1),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR,
                                                                        old_value=0,
                                                                        new_value=0),
                                                              mock.call(account_id=self.account2.id,
                                                                        type=ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST,
                                                                        old_value=0,
                                                                        new_value=0)])
