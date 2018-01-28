
import uuid

from unittest import mock

from dext.common.utils.urls import url

from django.conf import settings as project_settings

from tt_protocol.protocol import timers_pb2

from tt_logic.cards import constants as logic_cards_constants

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.accounts import tt_api as accounts_tt_api
from the_tale.accounts import relations as accounts_relations

from the_tale.game.logic import create_test_map
from the_tale.game import names

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.places import logic as places_logic

from .. import relations
from .. import objects
from .. import tt_api
from .. import logic
from .. import cards


class CardsRequestsTestsBase(testcase.TestCase):

    def setUp(self):
        super(CardsRequestsTestsBase, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        tt_api.debug_clear_service()

        self.card = objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        self.building_1 = places_logic.create_building(person=self.place_1.persons[0], utg_name=names.generator().get_test_name('building-1-name'))


class UseDialogRequestTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['common.login_required'])

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['pgf-error-card.wrong_value'])

    def test_has_cards(self):
        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=self.card.uid)))

    def test_every_card(self):
        self.request_login(self.account.email)

        for card_type in cards.CARD.records:
            if card_type in (cards.CARD.GET_COMPANION_UNCOMMON,
                             cards.CARD.GET_COMPANION_RARE,
                             cards.CARD.GET_COMPANION_EPIC,
                             cards.CARD.GET_COMPANION_LEGENDARY):
                continue

            card = card_type.effect.create_card(available_for_auction=True, type=card_type)
            tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

            self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=self.card.uid)))


class UseRequestTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(uuid.uuid4().hex), {}), 'common.login_required')

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(uuid.uuid4().hex)), 'card.wrong_value')

    def test_form_invalid(self):
        self.request_login(self.account.email)

        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(self.card.uid), {'value': 6666666}), 'form_errors')

    def test_success(self):
        self.request_login(self.account.email)

        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        response = self.post_ajax_json(logic.use_card_url(self.card.uid), {'value': self.place_1.id})
        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        task.remove()


class TestIndexRequests(CardsRequestsTestsBase):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_simple(self):
        texts = [card.text for card in cards.CARD.records]
        self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)

    def test_rarity_filter(self):
        for rarity in relations.RARITY.records:
            texts = [card.text for card in cards.CARD.records if card.rarity == rarity]
            self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)

    def test_availability_filter(self):
        for availability in relations.AVAILABILITY.records:
            texts = [card.text for card in cards.CARD.records if card.availability == availability]
            self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)


class GetCardRequestsTests(CardsRequestsTestsBase):

    def setUp(self):
        super(GetCardRequestsTests, self).setUp()

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.receive_cards_url()), 'common.login_required')

    def test_no_new_cards(self):
        self.request_login(self.account.email)

        response = self.post_ajax_json(logic.receive_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(data['cards'], [])

    def test_has_new_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        tt_api.change_cards(account_id=self.account.id,
                            operation_type='#test',
                            storage=relations.STORAGE.NEW,
                            to_add=cards)

        response = self.post_ajax_json(logic.receive_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(len(data['cards']), 2)

        self.assertEqual({card.uid.hex for card in cards},
                         {card['uid'] for card in data['cards']})


class CombineCardsRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url()), 'common.login_required')

    def test_created(self):
        self.request_login(self.account.email)

        card_1 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2])

        response = self.post_ajax_json(logic.combine_cards_url(), {'card': [card_1.uid, card_2.uid]})

        account_cards = tt_api.load_cards(self.hero.account_id)

        self.assertEqual(len(account_cards), 1)

        new_card = list(account_cards.values())[0]

        data = self.check_ajax_ok(response)

        self.assertEqual(data['card'], new_card.ui_info())

    def test_wrong_cards(self):
        self.request_login(self.account.email)

        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url(), {'card': [uuid.uuid4().hex]}),
                                  'card.wrong_value')


class MoveToStorageRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url()), 'common.login_required')

    def test_move(self):
        self.request_login(self.account.email)
        card_1 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_3 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2, card_3])

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertFalse(any(card['in_storage'] for card in data['cards']))

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card_1.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))

        for card in data['cards']:
            if card['uid'] in (card_1.uid.hex, card_3.uid.hex):
                self.assertTrue(card['in_storage'])
            else:
                self.assertFalse(card['in_storage'])

    def test_already_moved(self):
        self.request_login(self.account.email)
        card = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex]}))
        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertTrue(data['cards'][0]['in_storage'])

    def test_no_card(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url(), {'card': [uuid.uuid4().hex]}), 'card.wrong_value')

    def test_no_card__in_list(self):
        self.request_login(self.account.email)
        card = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex, uuid.uuid4().hex]}), 'card.wrong_value')


class MoveToHandRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url()), 'common.login_required')

    def test_move(self):
        self.request_login(self.account.email)
        card_1 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_3 = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2, card_3])
        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card_1.uid.hex, card_2.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertTrue(any(card['in_storage'] for card in data['cards']))

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card_1.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))

        for card in data['cards']:
            if card['uid'] in (card_1.uid.hex, card_3.uid.hex):
                self.assertFalse(card['in_storage'])
            else:
                self.assertTrue(card['in_storage'])

    def test_already_moved(self):
        self.request_login(self.account.email)
        card = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertFalse(data['cards'][0]['in_storage'])

    def test_no_card(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url(), {'card': [uuid.uuid4().hex]}), 'card.wrong_value')

    def test_no_card__in_list(self):
        self.request_login(self.account.email)
        card = objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        tt_api.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card.uid.hex, uuid.uuid4().hex]}), 'card.wrong_value')


class TakeCardCallbackTests(CardsRequestsTestsBase):

    def create_data(self, secret):
        timers = accounts_tt_api.get_owner_timers(self.account.id)

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        return timers_pb2.CallbackBody(timer=timers_pb2.Timer(owner_id=self.account.id,
                                                              entity_id=0,
                                                              type=0,
                                                              speed=new_card_timer.speed),
                                       callback_data='xy',
                                       secret=secret).SerializeToString()

    def test_no_post_data(self):
        self.check_ajax_error(self.post_ajax_json(url('game:cards:tt-take-card-callback')), 'common.wrong_tt_post_data', status_code=500)

        cards = tt_api.load_cards(self.account.id)
        self.assertEqual(cards, {})

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')
        self.check_ajax_error(self.post_ajax_binary(url('game:cards:tt-take-card-callback'), data), 'common.wrong_tt_secret', status_code=500)

        cards = tt_api.load_cards(self.account.id)
        self.assertEqual(cards, {})

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_does_not_participate_in_game(self):
        data = self.create_data(secret=project_settings.TT_SECRET)
        self.check_ajax_error(self.post_ajax_binary(url('game:cards:tt-take-card-callback'), data), 'common.player_does_not_participate_in_game')

        cards = tt_api.load_cards(self.account.id)
        self.assertEqual(cards, {})

    def check_cards_timer_speed(self, speed):
        timers = accounts_tt_api.get_owner_timers(self.account.id)

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        self.assertEqual(new_card_timer.speed, speed)

    def test_premium(self):

        self.check_cards_timer_speed(logic_cards_constants.NORMAL_PLAYER_SPEED)

        self.account.prolong_premium(30)
        self.account.save()

        data = self.create_data(secret=project_settings.TT_SECRET)
        self.check_ajax_ok(self.post_ajax_binary(url('game:cards:tt-take-card-callback'), data))

        cards = tt_api.load_cards(self.account.id)
        self.assertEqual(len(cards), 1)
        self.assertTrue(list(cards.values())[0].storage.is_NEW)
        self.assertTrue(list(cards.values())[0].available_for_auction)

        self.check_cards_timer_speed(logic_cards_constants.PREMIUM_PLAYER_SPEED)

    def test_not_premium(self):

        accounts_tt_api.change_cards_timer_speed(account_id=self.account.id,
                                                 speed=logic_cards_constants.PREMIUM_PLAYER_SPEED)

        self.check_cards_timer_speed(logic_cards_constants.PREMIUM_PLAYER_SPEED)

        data = self.create_data(secret=project_settings.TT_SECRET)
        self.check_ajax_ok(self.post_ajax_binary(url('game:cards:tt-take-card-callback'), data))

        cards = tt_api.load_cards(self.account.id)
        self.assertEqual(len(cards), 1)
        self.assertTrue(list(cards.values())[0].storage.is_NEW)
        self.assertFalse(list(cards.values())[0].available_for_auction)

        self.check_cards_timer_speed(logic_cards_constants.NORMAL_PLAYER_SPEED)


class GetCardsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.request_ajax_json(logic.get_cards_url()), 'common.login_required')

    def test_no_cards(self):
        self.request_login(self.account.email)

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(data['cards'], [])
        self.assertEqual(data['new_cards'], 0)
        self.assertEqual(data['new_card_timer'], {'border': logic_cards_constants.RECEIVE_TIME,
                                                  'finish_at': data['new_card_timer']['finish_at'],
                                                  'id': data['new_card_timer']['id'],
                                                  'owner_id': self.account.id,
                                                  'resources': 0.0,
                                                  'resources_at': data['new_card_timer']['resources_at'],
                                                  'speed': 1.0,
                                                  'type': accounts_relations.PLAYER_TIMERS_TYPES.CARDS_MINER.value})

    def test_has_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        tt_api.change_cards(account_id=self.account.id,
                            operation_type='#test',
                            storage=relations.STORAGE.FAST,
                            to_add=cards)

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(len(data['cards']), 2)

        self.assertEqual({card.uid.hex for card in cards},
                         {card['uid'] for card in data['cards']})

    def test_has_not_received_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        tt_api.change_cards(account_id=self.account.id,
                            operation_type='#test',
                            storage=relations.STORAGE.NEW,
                            to_add=cards)

        visible_card = logic.create_card(allow_premium_cards=True, available_for_auction=True)

        tt_api.change_cards(account_id=self.account.id,
                            operation_type='#test',
                            storage=relations.STORAGE.FAST,
                            to_add=[visible_card])

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)

        self.assertEqual(data['new_cards'], 2)
        self.assertEqual(len(data['cards']), 1)

        self.assertEqual(visible_card.uid.hex, data['cards'][0]['uid'])
