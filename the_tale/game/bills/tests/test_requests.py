# coding: utf-8
import datetime

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils.urls import url
from dext.common.meta_relations import logic as meta_relations_logic

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.forum.models import Post

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game.heroes import logic as heroes_logic


from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.places.relations import RESOURCE_EXCHANGE_TYPE

from ..models import Bill, Vote
from ..relations import VOTE_TYPE, BILL_STATE
from ..prototypes import BillPrototype, VotePrototype
from ..bills import PlaceRenaming, PersonRemove, PlaceResourceExchange
from ..conf import bills_settings
from .. import meta_relations


class BaseTestRequests(TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()

        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)
        self.account1.prolong_premium(30)
        self.account1._model.created_at -= datetime.timedelta(days=bills_settings.MINIMUM_BILL_OWNER_AGE)
        self.account1.save()

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)
        self.account2.prolong_premium(30)
        self.account2._model.created_at -= datetime.timedelta(days=bills_settings.MINIMUM_BILL_OWNER_AGE)
        self.account2.save()

        self.client = client.Client()

        self.request_login('test_user1@test.com')

        from the_tale.forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='Category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

    def create_bills(self, number, owner, caption_template, rationale_template, bill_data):
        return [BillPrototype.create(owner, caption_template % i, rationale_template % i, bill_data, chronicle_on_accepted='chronicle-on-accepted-%d' % i) for i in xrange(number) ]

    def check_bill_votes(self, bill_id, votes_for, votes_against):
        bill = Bill.objects.get(id=bill_id)
        self.assertEqual(bill.votes_for, votes_for)
        self.assertEqual(bill.votes_against, votes_against)

    def check_vote(self, vote, owner, type, bill_id):
        self.assertEqual(vote.owner, owner)
        self.assertEqual(vote.type, type)
        self.assertEqual(vote._model.bill.id, bill_id)


class TestIndexRequests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-unlogined-message', 1),))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-can-not-participate-in-politics', 1),
                                                                             ('pgf-unlogined-message', 0),))

    def test_no_bills(self):
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-no-bills-message', 1),))

    def test_bill_creation_locked_message(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 1),
                                                                             ('pgf-create-new-bill-buttons', 0),
                                                                             ('pgf-can-not-participate-in-politics', 0)))

    def test_bill_creation_unlocked_message(self):
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 0),
                                                                           ('pgf-create-new-bill-buttons', 1),
                                                                           ('pgf-can-not-participate-in-politics', 0)))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test_can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 0),
                                                                             ('pgf-create-new-bill-buttons', 0),
                                                                             ('pgf-can-not-participate-in-politics', 1)))

    def test_one_page(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(2, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(3, self.account2, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)

        texts = [('pgf-no-bills-message', 0),
                 ('Caption-a1-0', 1), ('rationale-a1-0', 0),
                 ('Caption-a1-1', 1), ('rationale-a1-1', 0),
                 ('Caption-a2-0', 1), ('rationale-a2-0', 0),
                 ('Caption-a2-1', 1), ('rationale-a2-1', 0),
                 ('Caption-a2-2', 1), ('rationale-a2-2', 0),
                 ('test_user1', 3),
                 ('test_user2', 3)]

        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=texts)

    def test_removed_bills(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)[0].remove(self.account1)

        self.check_html_ok(self.request_html(reverse('game:bills:')), texts=(('pgf-no-bills-message', 1),))

    def create_two_pages(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(bills_settings.BILLS_ON_PAGE, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)

        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(3, self.account2, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)

    def test_two_pages(self):
        self.create_two_pages()

        texts = [('pgf-no-bills-message', 0),
                 ('Caption-a1-0', 1), ('rationale-a1-0', 0),
                 ('Caption-a1-1', 1), ('rationale-a1-1', 0),
                 ('Caption-a1-2', 1), ('rationale-a1-2', 0),
                 ('Caption-a1-3', 0), ('rationale-a1-3', 0),
                 ('Caption-a2-0', 0), ('rationale-a2-0', 0),
                 ('Caption-a2-2', 0), ('rationale-a2-2', 0),
                 ('test_user1', 4), ('test_user2', 0)]

        self.check_html_ok(self.request_html(reverse('game:bills:')+'?page=2'), texts=texts)

    def test_index_redirect_from_large_page(self):
        self.assertRedirects(self.request_html(reverse('game:bills:')+'?page=2'),
                             reverse('game:bills:')+'?page=1', status_code=302, target_status_code=200)

    def test_filter_by_user_no_bills_message(self):
        self.create_two_pages()

        result, account_id, bundle_id = register_user('test_user4', 'test_user4@test.com', '111111')
        account4 = AccountPrototype.get_by_id(account_id)
        self.check_html_ok(self.request_html(reverse('game:bills:')+('?owner=%d' % account4.id)),
                           texts=[('pgf-no-bills-message', 1)])


    def test_filter_by_user(self):
        self.create_two_pages()

        account_1_texts = [('pgf-no-bills-message', 0),
                           ('Caption-a1-0', 1),
                           ('Caption-a1-1', 1),
                           ('Caption-a1-2', 1),
                           ('Caption-a1-3', 1),
                           ('Caption-a2-0', 0),
                           ('Caption-a2-2', 0),
                           ('test_user1', bills_settings.BILLS_ON_PAGE + 2), #1 for main menu, 1 for filter text
                           ('test_user2', 0)]

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?owner=%d' % self.account1.id)),
                           texts=account_1_texts)

        account_2_texts = [('pgf-no-bills-message', 0),
                           ('Caption-a1-0', 0),
                           ('Caption-a1-1', 0),
                           ('Caption-a1-2', 0),
                           ('Caption-a1-3', 0),
                           ('Caption-a2-0', 1),
                           ('Caption-a2-2', 1),
                           ('test_user1', 1), # 1 for main menu
                           ('test_user2', 3+1)] # 1 for filter text


        self.check_html_ok(self.request_html(reverse('game:bills:')+('?owner=%d' % self.account2.id)),
                           texts=account_2_texts)

    def test_filter_by_state(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        bill_voting, bill_accepted, bill_rejected = self.create_bills(3, self.account1, 'Caption-%d', 'rationale-%d', bill_data)

        bill_accepted.state = BILL_STATE.ACCEPTED
        bill_accepted._model.voting_end_at = datetime.datetime.now()
        bill_accepted.applyed_at_turn = 0
        bill_accepted.save()

        bill_rejected.state = BILL_STATE.REJECTED
        bill_rejected._model.voting_end_at = datetime.datetime.now()
        bill_rejected.applyed_at_turn = 0
        bill_rejected.save()

        def check_state_filter(self, state, voting_number, accepted_number, rejected_number):
            url = reverse('game:bills:')
            if state is not None:
                url += ('?state=%d' % state.value)
            self.check_html_ok(self.request_html(url),
                               texts=[('Caption-0', voting_number),
                                      ('Caption-1', accepted_number),
                                      ('Caption-2', rejected_number)])

        check_state_filter(self, BILL_STATE.VOTING, 1, 0, 0)
        check_state_filter(self, BILL_STATE.ACCEPTED, 0, 1, 0)
        check_state_filter(self, BILL_STATE.REJECTED, 0, 0, 1)
        check_state_filter(self, None, 1, 1, 1)

    def test_filter_by_type_no_bills_message(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', 'rationale-%d', bill_data)

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?bill_type=%d' % PersonRemove.type.value)),
                           texts=[('pgf-no-bills-message', 1)])

    def test_filter_by_type(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', 'rationale-%d', bill_data)

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?bill_type=%d' % PlaceRenaming.type.value)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 1),
                                  ('Caption-1', 1),
                                  ('Caption-2', 1)])

    def test_filter_by_place_no_bills_message(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', 'rationale-%d', bill_data)

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?place=%d' % self.place2.id)),
                           texts=[('pgf-no-bills-message', 1)])

    def test_filter_by_place(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', 'rationale-%d', bill_data)

        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-2-%d', 'rationale-2-%d', bill_data)

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?place=%d' % self.place1.id)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 1),
                                  ('Caption-1', 1),
                                  ('Caption-2', 1),
                                  ('Caption-2-0', 0),
                                  ('Caption-2-1', 0),
                                  ('Caption-2-2', 0)])

        self.check_html_ok(self.request_html(reverse('game:bills:')+('?place=%d' % self.place2.id)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 0),
                                  ('Caption-1', 0),
                                  ('Caption-2', 3),
                                  ('Caption-2-0', 1),
                                  ('Caption-2-1', 1),
                                  ('Caption-2-2', 1)])


class TestNewRequests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        url_ = reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)
        self.check_redirect(url_, login_page_url(url_))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)), texts=(('common.fast_account', 1),))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)),
                           texts=(('bills.can_not_participate_in_politics', 1),))

    def test__banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)),
                           texts=(('common.ban_game', 1),))

    def test_wrong_type(self):
        self.check_html_ok(self.request_html(reverse('game:bills:new') + '?bill_type=xxx'), texts=(('bills.new.bill_type.wrong_format', 1),))

    def test_success(self):
        self.check_html_ok(self.request_html(reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)), texts=[])

    def test_new_place_renaming(self):
        texts = [('>'+place.name+'<', 1) for place in places_storage.all()]
        self.check_html_ok(self.request_html(reverse('game:bills:new') + ('?bill_type=%s' % PlaceRenaming.type.value)), texts=texts)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)
        self.hero.places_history.add_place(self.place1.id)
        self.hero.places_history.add_place(self.place2.id)
        self.hero.places_history.add_place(self.place3.id)
        heroes_logic.save_hero(self.hero)


    def test_unlogined(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.request_logout()
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-unlogined-message', 1),))

    def test_is_fast(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account2, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.account1.is_fast = True
        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 1),))

    def test_can_not_participate_in_politics(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account2, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 1),))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_not_participate_in_politics__voted(self):
        # one vote automaticaly created for bill author
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 0),))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_not_vote(self):
        self.hero.places_history._reset()
        heroes_logic.save_hero(self.hero)

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account2, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-vote-message', 1),))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_not_voted(self):
        self.assertEqual(heroes_logic.load_hero(account_id=self.account1.id).places_history.history, [])

        # one vote automaticaly created for bill author
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-vote-message', 0),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[0])), status_code=404)

    def test_removed(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_1'))
        bill = self.create_bills(1, self.account1, 'Caption-a1-%d', 'rationale-a1-%d', bill_data)[0]
        bill.remove(self.account1)
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=[('bills.removed', 1)])

    def test_show(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        texts = [('Caption-a2-0', 3 + 1), # 1 from social sharing
                 ('rationale-a2-0', 1 + 1), # 1 from social sharing
                 ('pgf-voting-block', 0),
                 ('pgf-forum-block', 1),
                 ('pgf-bills-results-summary', 1),
                 ('pgf-bills-results-detailed', 0),
                 ('pgf-can-not-vote-message', 0),
                 (self.place2.name, 2)]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)


    def test_show__folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = BillPrototype._db_latest()

        blogs_helpers.create_post_for_meta_object(self.account1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Bill.create_from_object(bill))
        blogs_helpers.create_post_for_meta_object(self.account1, 'folclor-2-caption', 'folclor-2-text', meta_relations.Bill.create_from_object(bill))

        texts = ['folclor-1-caption',
                 'folclor-1-text',
                 'folclor-2-caption']

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)


    def test_show__vote_for(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        texts = [('pgf-voted-for-marker', 1),
                 ('pgf-voted-against-marker', 0),
                 ('pgf-voted-refrained-marker', 0),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__vote_against(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        VotePrototype._model_class.objects.all().update(type=VOTE_TYPE.AGAINST)

        texts = [('pgf-voted-for-marker', 0),
                 ('pgf-voted-against-marker', 1),
                 ('pgf-voted-refrained-marker', 0),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__vote_refrained(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        VotePrototype._model_class.objects.all().update(type=VOTE_TYPE.REFRAINED)

        texts = [('pgf-voted-for-marker', 0),
                 ('pgf-voted-against-marker', 0),
                 ('pgf-voted-refrained-marker', 1),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)


    def test_show_when_not_voting_state(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]
        bill.state = BILL_STATE.ACCEPTED
        bill.voting_end_at = datetime.datetime.now()
        bill.applyed_at_turn = 0
        bill.save()

        texts = [('pgf-bills-results-summary', 0),
                 ('pgf-bills-results-detailed', 1)]

        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show_after_voting(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, name_forms=names.generator.get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        texts = [('pgf-voting-block', 1),
                 ('test-already-voted-block', 0),
                 (self.place2.name, 2)]

        self.request_logout()
        self.request_login('test_user2@test.com')
        self.check_html_ok(self.request_html(reverse('game:bills:show', args=[bill.id])), texts=texts)


class TestCreateRequests(BaseTestRequests):

    def get_post_data(self):
        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})
        return data

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'common.fast_account')

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test___can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'bills.can_not_participate_in_politics')

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'common.ban_game')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:create') + '?bill_type=xxx', self.get_post_data()), 'bills.create.bill_type.wrong_format')

    def test_success(self):
        response = self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), self.get_post_data())

        bill = BillPrototype(Bill.objects.all()[0])
        self.assertEqual(bill.caption, 'bill-caption')
        self.assertEqual(bill.rationale, 'bill-rationale')
        self.assertEqual(bill.data.place.id, self.place1.id)
        self.assertEqual(bill.data.base_name, u'new-name-нс,ед,им')
        self.assertEqual(bill.votes_for, 1)
        self.assertEqual(bill.votes_against, 0)
        self.assertEqual(bill.chronicle_on_accepted, 'chronicle-on-accepted')

        vote = VotePrototype(Vote.objects.all()[0])
        self.check_vote(vote, self.account1, VOTE_TYPE.FOR, bill.id)

        self.check_ajax_ok(response, data={'next_url': reverse('game:bills:show', args=[bill.id])})

    def test_success_second_bill_error(self):
        self.check_ajax_ok(self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), self.get_post_data()))
        self.check_ajax_error(self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), self.get_post_data()),
                              'bills.create.active_bills_limit_reached')
        self.assertEqual(Bill.objects.all().count(), 1)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MINIMUM_BILL_OWNER_AGE', bills_settings.MINIMUM_BILL_OWNER_AGE + 1)
    def test_too_young(self):
        with self.check_not_changed(BillPrototype._db_count):
            self.check_ajax_error(self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), self.get_post_data()),
                                  'bills.create.too_young_owner')



class TestVoteRequests(BaseTestRequests):

    def setUp(self):
        super(TestVoteRequests, self).setUp()

        self.account2.prolong_premium(30)
        self.account2.save()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)
        self.hero.places_history.add_place(self.place1.id)
        self.hero.places_history.add_place(self.place2.id)
        self.hero.places_history.add_place(self.place3.id)

        heroes_logic.save_hero(self.hero)

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])

        self.request_logout()
        self.request_login('test_user2@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'common.fast_account')
        self.check_bill_votes(self.bill.id, 1, 0)

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'bills.can_not_participate_in_politics')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test___banned(self):
        self.account2.ban_game(30)
        self.account2.save()
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'common.ban_game')
        self.check_bill_votes(self.bill.id, 1, 0)


    def test_bill_not_exists(self):
        self.check_ajax_error(self.client.post(url('game:bills:vote', 666, type=VOTE_TYPE.FOR.value), {}), 'bills.bill.not_found')

    def test_wrong_value(self):
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type='bla-bla'), {}), 'bills.vote.type.wrong_format')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_bill_accepted(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'bills.voting_state_required')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_bill_rejected(self):
        self.bill.state = BILL_STATE.REJECTED
        self.bill.save()
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'bills.voting_state_required')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_success_for(self):
        self.check_ajax_ok(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}))
        vote = VotePrototype(Vote.objects.all()[1])
        self.check_vote(vote, self.account2, VOTE_TYPE.FOR, self.bill.id)
        self.check_bill_votes(self.bill.id, 2, 0)

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_new', False)
    def test_can_not_vote(self):
        self.hero.places_history._reset()
        heroes_logic.save_hero(self.hero)

        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'bills.vote.can_not_vote')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_success_agains(self):
        self.check_ajax_ok(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.AGAINST.value), {}))
        vote = VotePrototype(Vote.objects.all()[1])
        self.check_vote(vote, self.account2, VOTE_TYPE.AGAINST, self.bill.id)
        self.check_bill_votes(self.bill.id, 1, 1)

    def test_already_exists(self):
        self.check_ajax_ok(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}))
        self.check_ajax_error(self.client.post(url('game:bills:vote', self.bill.id, type=VOTE_TYPE.FOR.value), {}), 'bills.vote.vote_exists')
        self.check_bill_votes(self.bill.id, 2, 0)


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])


    def test_unlogined(self):
        self.request_logout()
        url = reverse('game:bills:edit', args=[self.bill.id])
        self.check_redirect(url, login_page_url(url))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=(('common.fast_account', 1),))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.can_not_participate_in_politics', 1),))

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=(('common.ban_game', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[666])), status_code=404)

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=[('bills.removed', 1)])

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user2@test.com')
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.not_owner', 1),))

    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.voting_state_required', 1),))

    def test_success(self):
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=['chronicle-on-accepted'])


    def test_edit_place_renaming(self):
        texts = [('>'+place.name+'<', 1) for place in places_storage.all()]
        self.check_html_ok(self.request_html(reverse('game:bills:edit', args=[self.bill.id])), texts=texts)


class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})


        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])

    def get_post_data(self):
        new_name = names.generator.get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'new-caption',
                     'rationale': 'new-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'place': self.place2.id})
        return data

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.fast_account')

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.can_not_participate_in_politics')

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.ban_game')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[666]), self.get_post_data()), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user2@test.com')
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.not_owner')

    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.voting_state_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:update', args=[self.bill.id]), {}), 'bills.update.form_errors')

    def test_update_success(self):
        old_updated_at = self.bill.updated_at

        self.assertEqual(Post.objects.all().count(), 1)

        self.check_ajax_ok(self.client.post(reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()))

        self.bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(old_updated_at < self.bill.updated_at)

        self.assertEqual(Post.objects.all().count(), 2)

        self.assertEqual(self.bill.chronicle_on_accepted, 'chronicle-on-accepted-2')

        self.bill._model.delete()


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])

        self.request_logout()
        self.request_login('test_user2@test.com')

        group = sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)


    def test_unlogined(self):
        self.request_logout()
        url = reverse('game:bills:moderate', args=[self.bill.id])
        self.check_redirect(url, login_page_url(url))

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[self.bill.id])), texts=(('common.fast_account', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[666])), status_code=404)

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[self.bill.id])), texts=[('bills.removed', 1)])

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user1@test.com')
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[self.bill.id])), texts=(('bills.moderator_rights_required', 1),))

    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[self.bill.id])), texts=(('bills.voting_state_required', 1),))

    def test_success(self):
        self.check_html_ok(self.request_html(reverse('game:bills:moderate', args=[self.bill.id])))


class TestModerateRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'place': self.place1.id,
                     'chronicle_on_accepted': 'chronicle-on-accepted'})

        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])

        self.request_logout()
        self.request_login('test_user2@test.com')

        group = sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)


    def get_post_data(self):
        data = linguistics_helpers.get_word_post_data(self.bill.data.name_forms, prefix='name')
        data.update({'approved': True})
        return data


    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'common.fast_account')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[666]), self.get_post_data()), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'bills.moderator_rights_required')

    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'bills.voting_state_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), {}), 'bills.moderate.form_errors')

    def test_moderate_success(self):
        self.check_ajax_ok(self.client.post(reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()))


class TestDeleteRequests(BaseTestRequests):

    def setUp(self):
        super(TestDeleteRequests, self).setUp()

        new_name = names.generator.get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'rationale': 'bill-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(reverse('game:bills:create') + ('?bill_type=%s' % PlaceRenaming.type.value), data)
        self.bill = BillPrototype(Bill.objects.all()[0])

        self.request_logout()
        self.request_login('test_user2@test.com')

        group = sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:bills:delete', args=[self.bill.id]), {}), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:delete', args=[self.bill.id]), {}), 'common.fast_account')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:delete', args=[666]), {}), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(reverse('game:bills:delete', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:bills:delete', args=[self.bill.id]), {}), 'bills.moderator_rights_required')

    def test_delete_success(self):
        self.check_ajax_ok(self.client.post(reverse('game:bills:delete', args=[self.bill.id]), {}))
