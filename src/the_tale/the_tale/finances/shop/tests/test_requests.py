
from unittest import mock

from dext.common.utils.urls import url
from dext.settings import settings

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.finances.bank.prototypes import InvoicePrototype as BankInvoicePrototype
from the_tale.finances.bank.tests.helpers import BankTestsMixin

from the_tale.game.logic import create_test_map

from the_tale.accounts.logic import login_page_url

from the_tale.game.cards import cards
from the_tale.game.cards import tt_api as cards_tt_api

from the_tale.finances.bank import prototypes as bank_prototypes
from the_tale.finances.bank import relations as bank_relations

from ..price_list import PURCHASES_BY_UID
from ..conf import payments_settings
from ..relations import PERMANENT_PURCHASE_TYPE
from ..goods import PermanentPurchase
from .. import logic
from .. import tt_api
from .. import objects

from the_tale.accounts.third_party.tests import helpers as third_party_helpers


class PageRequestsMixin(object):

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(self.page_url), texts=['common.fast_account'])

    def test_refuse_third_party__profile_page(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(url('accounts:profile:show')), texts=['third_party.access_restricted'])


    def test_unlogined(self):
        self.request_logout()
        self.check_redirect(self.page_url, login_page_url(self.page_url))

    def test_xsolla_buy_link(self):
        self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-xsolla-dialog-link', 1)])

    @mock.patch('the_tale.finances.shop.conf.payments_settings.XSOLLA_ENABLED', False)
    def test_xsolla_disabled__xsolla(self):
        self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('the_tale.finances.shop.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('the_tale.finances.shop.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_xsolla_disabled__global(self):
        self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-xsolla-dialog-link', 0)])

    def test_xsolla_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('the_tale.finances.shop.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_xsolla_disabled__global_with_exception(self):
        with mock.patch('the_tale.finances.shop.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-xsolla-dialog-link', 1)])


class RequestesTestsBase(testcase.TestCase, third_party_helpers.ThirdPartyTestsMixin):

    def setUp(self):
        super(RequestesTestsBase, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        settings[payments_settings.SETTINGS_ALLOWED_KEY] = 'allowed'

        self.request_login(self.account.email)

        tt_api.debug_clear_service()


    def tearDown(self):
        super().tearDown()
        tt_api.debug_clear_service()


class ShopRequestesTests(RequestesTestsBase, PageRequestsMixin, BankTestsMixin):

    def setUp(self):
        super(ShopRequestesTests, self).setUp()
        self.page_url = url('shop:')
        self.create_bank_account(self.account.id, amount=666666)

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(self.page_url), texts=['third_party.access_restricted'])


    def test_goods(self):
        self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-no-goods-message', 0)] + list(PURCHASES_BY_UID.keys()))

    def test_purchasable_items(self):
        for purchase in list(PURCHASES_BY_UID.values()):
            if not isinstance(purchase, PermanentPurchase):
                continue

            self.account.permanent_purchases.insert(purchase.purchase_type)
            self.account.save()

            existed_uids = list(PURCHASES_BY_UID.keys())
            existed_uids.remove(purchase.uid)

            if purchase.purchase_type.is_INFINIT_SUBSCRIPTION:
                existed_uids = [uid for uid in existed_uids if not uid.startswith('subscription-')]

            self.check_html_ok(self.request_html(self.page_url), texts=[('pgf-no-goods-message', 0), (purchase.uid, 0)] + existed_uids )

            self.account.permanent_purchases._data = set()
            self.account.save()


class HistoryRequestesTests(RequestesTestsBase, BankTestsMixin, PageRequestsMixin):

    def setUp(self):
        super(HistoryRequestesTests, self).setUp()
        self.page_url = url('shop:history')

    def test_no_history(self):
        self.check_html_ok(self.request_html(self.page_url), texts=['pgf-no-history-message'])

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(self.page_url), texts=['third_party.access_restricted'])


    def test_history(self):
        self.create_bank_account(self.account.id)
        history = self.create_entity_history(self.account.id)
        invoices = BankInvoicePrototype._db_all()

        histroy_ids = [invoice.id for invoice in history]

        texts = [('pgf-no-history-message', 0)]

        for invoice in invoices:
            if invoice.id in histroy_ids:
                continue

            if invoice.recipient_id == self.account.id:
                texts.append((invoice.description_for_recipient, 0))
            else:
                texts.append((invoice.description_for_sender, 0))

        for invoice in history:
            if invoice.recipient_id == self.account.id:
                texts.append((invoice.description_for_recipient, 1))
                texts.append((invoice.description_for_sender, 0))
            else:
                texts.append((invoice.description_for_recipient, 0))
                texts.append((invoice.description_for_sender, 1))

        self.check_html_ok(self.request_html(self.page_url), texts=texts)


    def test_no_purchases(self):
        self.check_html_ok(self.request_html(self.page_url), texts=['pgf-no-permanent-purchases-message'])

    def test_purchases(self):

        texts = []

        for record in PERMANENT_PURCHASE_TYPE.records:
            self.account.permanent_purchases.insert(record)
            texts.append(record.description)
            texts.append(record.text)
        self.account.save()

        self.check_html_ok(self.request_html(self.page_url), texts=texts)



class BuyRequestesTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(BuyRequestesTests, self).setUp()

        self.purchase = list(PURCHASES_BY_UID.values())[0]

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('shop:buy', purchase=self.purchase.uid)), 'common.fast_account')

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        self.check_ajax_error(self.client.post(url('shop:buy', purchase=self.purchase.uid)), 'third_party.access_restricted')


    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('shop:buy', purchase=self.purchase.uid)), 'common.login_required')

    def test_wrong_purchase_uid(self):
        self.check_ajax_error(self.client.post(url('shop:buy', purchase='wrong-uid')), 'purchase.wrong_value')

    def test_success(self):
        response = self.client.post(url('shop:buy', purchase=self.purchase.uid))
        self.check_ajax_processing(response, PostponedTaskPrototype._db_get_object(0).status_url)


class CreateSellLotTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(CreateSellLotTests, self).setUp()

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.cards = [cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP),
                      cards.CARD.ADD_GOLD_COMMON.effect.create_card(available_for_auction=True, type=cards.CARD.ADD_GOLD_COMMON)]

        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=self.cards)


    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})
        self.check_ajax_error(response, 'common.fast_account')

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})
        self.check_ajax_error(response, 'third_party.access_restricted')

    def test_unlogined(self):
        self.request_logout()
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})
        self.check_ajax_error(response, 'common.login_required')

    def test_no_cards(self):
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'price': 100})
        self.check_ajax_error(response, 'card.not_specified')


    def test_no_cards_in_storage(self):
        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_remove=[self.cards[0]])
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'cards': [self.cards[0].uid, self.cards[1].uid], 'price': 100})
        self.check_ajax_error(response, 'card.not_specified')


    def test_no_price(self):
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid]})
        self.check_ajax_error(response, 'price.not_specified')


    def test_wrong_price(self):
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': payments_settings.MINIMUM_MARKET_PRICE-1})
        self.check_ajax_error(response, 'price.wrong_value')


    def test_not_tradable_card(self):
        wrong_card = cards.CARD.CANCEL_QUEST.effect.create_card(available_for_auction=False, type=cards.CARD.CANCEL_QUEST)
        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=[wrong_card])
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid, wrong_card.uid], 'price': 100})
        self.check_ajax_error(response, 'not_available_for_auction')


    def test_success(self):
        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})
        self.check_ajax_ok(response)


class InfoTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(InfoTests, self).setUp()

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.cards = [cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP),
                      cards.CARD.ADD_GOLD_COMMON.effect.create_card(available_for_auction=True, type=cards.CARD.ADD_GOLD_COMMON)]

        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=self.cards)

        self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})


    def test_success(self):
        response = self.request_ajax_json(logic.info_url())
        data = self.check_ajax_ok(response)

        self.assertCountEqual(data, {'info': [{'min_sell_price': 100,
                                               'max_sell_price': 100,
                                               'sell_number': 1,
                                               'item_type': '1'},
                                              {'min_sell_price': 100,
                                               'max_sell_price': 100,
                                               'sell_number': 1,
                                               'item_type': '10'}],
                                    'account_balance': 0})


class ItemTypePricesTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super().setUp()

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.cards = [cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP),
                      cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP),
                      cards.CARD.ADD_GOLD_COMMON.effect.create_card(available_for_auction=True, type=cards.CARD.ADD_GOLD_COMMON)]

        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=self.cards)

        self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[2].uid], 'price': 10})
        self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[1].uid], 'price': 100})


    def test_no_item_type(self):
        response = self.request_ajax_json(logic.item_type_prices_url())
        self.check_ajax_error(response, 'item_type.not_specified')


    def test_success(self):
        response = self.request_ajax_json(logic.item_type_prices_url()+'?item_type={}'.format(self.cards[0].item_full_type))
        data = self.check_ajax_ok(response)

        self.assertEqual(data, {'prices': {'10': 1, '100': 1}, 'owner_prices': {'10': 1, '100': 1}})


    def test_success__no_owner(self):

        self.request_logout()

        account_2 = self.accounts_factory.create_account()

        self.request_login(account_2.email)

        response = self.request_ajax_json(logic.item_type_prices_url()+'?item_type={}'.format(self.cards[0].item_full_type))
        data = self.check_ajax_ok(response)

        self.assertEqual(data, {'prices': {'10': 1, '100': 1}, 'owner_prices': {}})


class GiveMoneyRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(GiveMoneyRequestesTests, self).setUp()

        self.superuser = self.accounts_factory.create_account(is_superuser=True)

        self.request_login(self.superuser.email)

    def post_data(self, amount=105):
        return {'amount': amount, 'description': 'bla-bla'}

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('shop:give-money', account=self.account.id), self.post_data()), 'fast_account')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        self.check_ajax_error(self.client.post(url('shop:give-money', account=self.account.id), self.post_data()), 'third_party.access_restricted')


    def test_for_wront_account(self):
        self.check_ajax_error(self.client.post(url('shop:give-money', account='xxx'), self.post_data()), 'account.wrong_format')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('shop:give-money', account=self.account.id), self.post_data()), 'common.login_required')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_from_errors(self):
        self.check_ajax_error(self.client.post(url('shop:give-money', account=self.account.id), {'amount': 'x', 'description': 'bla-bla'}),
                              'form_errors')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_success(self):
        self.assertEqual(BankInvoicePrototype._db_count(), 0)
        response = self.post_ajax_json(url('shop:give-money', account=self.account.id), self.post_data(amount=5))
        self.assertEqual(BankInvoicePrototype._db_count(), 1)

        invoice = BankInvoicePrototype._db_get_object(0)

        self.assertTrue(invoice.recipient_type.is_GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertTrue(invoice.sender_type.is_GAME_MASTER)
        self.assertEqual(invoice.sender_id, self.superuser.id)
        self.assertTrue(invoice.currency.is_PREMIUM)
        self.assertEqual(invoice.amount, 5)
        self.assertEqual(invoice.description_for_recipient, 'bla-bla')
        self.assertTrue(invoice.state.is_FORCED)

        self.check_ajax_ok(response)


class CloseSellLotTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(CloseSellLotTests, self).setUp()

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.card = cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP)

        self.bank_account = bank_prototypes.AccountPrototype.create(entity_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                    entity_id=self.account.id,
                                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM)
        self.bank_account.amount = 1000
        self.bank_account.save()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'common.fast_account')

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'third_party.access_restricted')

    def test_unlogined(self):
        self.request_logout()
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'common.login_required')

    def test_no_price(self):
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type})
        self.check_ajax_error(response, 'price.not_specified')

    def test_no_type(self):
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'price': 666})
        self.check_ajax_error(response, 'item_type.not_specified')

    def test_wrong_price(self):
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': payments_settings.MINIMUM_MARKET_PRICE-1})
        self.check_ajax_error(response, 'price.wrong_value')


    def test_no_money(self):
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 10000})
        self.check_ajax_error(response, 'not_enough_money')

    def test_success(self):
        response = self.post_ajax_json(logic.close_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.item_type, self.card.item_full_type)
        self.assertEqual(task.internal_logic.price, 100)

        invoice = bank_prototypes.InvoicePrototype._db_get_object(0)

        self.assertEqual(invoice.recipient_type, bank_relations.ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.recipient_id, 0)
        self.assertEqual(invoice.sender_type, bank_relations.ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.sender_id, self.account.id)
        self.assertEqual(invoice.currency, bank_relations.CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, 100)
        self.assertEqual(invoice.description_for_sender, 'Покупка «%s»' % self.card.name)
        self.assertEqual(invoice.description_for_recipient, 'Продажа «%s»' % self.card.name)
        self.assertEqual(invoice.operation_uid, 'market-buy-lot-cards-hero-good')


class CancelSellLotTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(CancelSellLotTests, self).setUp()

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.card = cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP)

        self.item_info = objects.ItemTypeSummary(full_type=self.card.item_full_type,
                                                 sell_number=1,
                                                 min_sell_price=100,
                                                 max_sell_price=100)

        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=[self.card])

        response = self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.card.uid], 'price': 100})
        self.check_ajax_ok(response)

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'common.fast_account')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_refuse_third_party(self):
        self.request_third_party_token(account=self.account)
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'third_party.access_restricted')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_unlogined(self):
        self.request_logout()
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_error(response, 'common.login_required')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_no_price(self):
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type})
        self.check_ajax_error(response, 'price.not_specified')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_no_type(self):
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'price': 666})
        self.check_ajax_error(response, 'item_type.not_specified')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_wrong_price(self):
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': payments_settings.MINIMUM_MARKET_PRICE-1})
        self.check_ajax_error(response, 'price.wrong_value')

        self.assertEqual(tt_api.info(), [self.item_info])
        self.assertNotIn(self.card.uid, cards_tt_api.load_cards(self.account.id))

    def test_success(self):
        response = self.post_ajax_json(logic.cancel_sell_lot_url(), {'item_type': self.card.item_full_type, 'price': 100})
        self.check_ajax_ok(response)

        self.assertEqual(tt_api.info(), [])
        self.assertIn(self.card.uid, cards_tt_api.load_cards(self.account.id))



class MarketHistoryTests(RequestesTestsBase, BankTestsMixin, PageRequestsMixin):

    def setUp(self):
        super(MarketHistoryTests, self).setUp()

        self.page_url = url('shop:market-history')

        tt_api.debug_clear_service()
        cards_tt_api.debug_clear_service()

        self.cards = [cards.CARD.LEVEL_UP.effect.create_card(available_for_auction=True, type=cards.CARD.LEVEL_UP),
                      cards.CARD.ADD_GOLD_COMMON.effect.create_card(available_for_auction=True, type=cards.CARD.ADD_GOLD_COMMON)]

        cards_tt_api.change_cards(self.account.id, operation_type='#test', to_add=self.cards)

        self.post_ajax_json(logic.create_sell_lot_url(), {'card': [self.cards[0].uid, self.cards[1].uid], 'price': 100})


    def test_success__no_history(self):
        self.check_html_ok(self.request_html(self.page_url))


    def test_success__has_history(self):
        for card in self.cards:
            tt_api.close_lot(item_type=card.item_full_type,
                             price=100,
                             buyer_id=666)

        self.check_html_ok(self.request_html(self.page_url))
