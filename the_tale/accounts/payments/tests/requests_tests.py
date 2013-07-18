# coding: utf-8

import mock

from dext.utils.urls import url
from dext.settings import settings

from common.utils import testcase
from common.postponed_tasks import PostponedTaskPrototype

from bank.prototypes import InvoicePrototype as BankInvoicePrototype
from bank.tests.helpers import BankTestsMixin
from bank.dengionline.prototypes import InvoicePrototype as DOInvoicePrototype
from bank.dengionline.conf import dengionline_settings

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from accounts.payments.price_list import PURCHASES_BY_UID
from accounts.payments.conf import payments_settings
from accounts.payments.logic import real_amount_to_game


class RequestesTestsBase(testcase.TestCase):

    def setUp(self):
        super(RequestesTestsBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        settings[payments_settings.SETTINGS_ALLOWED_KEY] = 'allowed'

        self.request_login(self.account.email)


class ShopRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(ShopRequestesTests, self).setUp()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=['common.fast_account'])

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:payments:shop')
        self.check_redirect(requested_url, login_url(requested_url))

    def test_buy_link(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-dengionline-dialog-link', 2)])

    @mock.patch('accounts.payments.conf.payments_settings.DENGIONLINE_ENABLED', False)
    def test_dengionline_disabled__dengionline(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-dengionline-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_dengionline_disabled__global(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-dengionline-dialog-link', 0)])

    def test_dengionline_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-dengionline-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_dengionline_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-dengionline-dialog-link', 2)])


    def test_xsolla_buy_link(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-xsolla-dialog-link', 1)])

    @mock.patch('accounts.payments.conf.payments_settings.XSOLLA_ENABLED', False)
    def test_xsolla_disabled__xsolla(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_xsolla_disabled__global(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-xsolla-dialog-link', 0)])

    def test_xsolla_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_xsolla_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-xsolla-dialog-link', 1)])

    @mock.patch('accounts.payments.price_list.PRICE_LIST', [])
    def test_no_goods(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=['pgf-no-goods-message'])

    def test_goods(self):
        self.check_html_ok(self.request_html(url('accounts:payments:shop')), texts=[('pgf-no-goods-message', 0)] + PURCHASES_BY_UID.keys())


class HistoryRequestesTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(HistoryRequestesTests, self).setUp()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=['common.fast_account'])

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:payments:history')
        self.check_redirect(requested_url, login_url(requested_url))

    def test_no_history(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=['pgf-no-history-message'])

    def test_history(self):
        self.create_bank_account(self.account.id)
        history = self.create_entity_history(self.account.id)
        invoices = BankInvoicePrototype._db_all()

        histroy_ids = [invoice.id for invoice in history]

        texts = [('pgf-no-history-message', 0)]

        for invoice in invoices:
            if invoice.id in histroy_ids:
                continue
            texts.append((invoice.description, 0))

        for invoice in history:
            texts.append((invoice.description, 1))

        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=texts)

    def test_dengionline_buy_link(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-dengionline-dialog-link', 2)])

    @mock.patch('accounts.payments.conf.payments_settings.DENGIONLINE_ENABLED', False)
    def test_dengionline_disabled__dengionline(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-dengionline-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_dengionline_disabled__global(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-dengionline-dialog-link', 0)])

    def test_dengionline_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-dengionline-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_dengionline_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-dengionline-dialog-link', 2)])

    def test_xsolla_buy_link(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-xsolla-dialog-link', 1)])

    @mock.patch('accounts.payments.conf.payments_settings.XSOLLA_ENABLED', False)
    def test_xsolla_disabled__xsolla(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_xsolla_disabled__global(self):
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-xsolla-dialog-link', 0)])

    def test_xsolla_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-xsolla-dialog-link', 0)])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_xsolla_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_html(url('accounts:payments:history')), texts=[('pgf-xsolla-dialog-link', 1)])



class BuyRequestesTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(BuyRequestesTests, self).setUp()

        self.purchase = PURCHASES_BY_UID.values()[0]

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('accounts:payments:buy', purchase=self.purchase.uid)), 'common.fast_account')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('accounts:payments:buy', purchase=self.purchase.uid)), 'common.login_required')

    def test_wrong_purchase_uid(self):
        self.check_ajax_error(self.client.post(url('accounts:payments:buy', purchase='wrong-uid')), 'payments.buy.purchase.not_found')

    def test_success(self):
        response = self.client.post(url('accounts:payments:buy', purchase=self.purchase.uid))
        self.check_ajax_processing(response, PostponedTaskPrototype._db_get_object(0).status_url)


class PayWithDengionlineRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(PayWithDengionlineRequestesTests, self).setUp()

    def post_data(self, amount):
        return {'real_amount': amount, 'game_amount': real_amount_to_game(amount)}

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('accounts:payments:pay-with-dengionline', amount=5)), 'common.fast_account')
        self.assertEqual(DOInvoicePrototype._db_count(), 0)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('accounts:payments:pay-with-dengionline', amount=5)), 'common.login_required')
        self.assertEqual(DOInvoicePrototype._db_count(), 0)

    def test_amount__wrong(self):
        self.check_ajax_error(self.client.post(url('accounts:payments:pay-with-dengionline'),
                                               {'real_amount': 'bla', 'game_amount': 10000}), 'payments.pay_with_dengionline.form_errors')
        self.assertEqual(DOInvoicePrototype._db_count(), 0)

    def test_amount__zero_or_less(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(-5)), 'payments.pay_with_dengionline.form_errors')
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(0)), 'payments.pay_with_dengionline.form_errors')
        self.assertEqual(DOInvoicePrototype._db_count(), 0)

    def test_amount__wrong_calculations(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'),
                                                  {'real_amount': 5, 'game_amount': real_amount_to_game(5)*2}), 'payments.pay_with_dengionline.form_errors')
        self.assertEqual(DOInvoicePrototype._db_count(), 0)

    def test_success(self):
        self.assertEqual(DOInvoicePrototype._db_count(), 0)
        response = self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5))
        self.assertEqual(DOInvoicePrototype._db_count(), 1)

        invoice = DOInvoicePrototype._db_get_object(0)

        self.assertTrue(invoice.bank_type._is_GAME_ACCOUNT)
        self.assertEqual(invoice.bank_id, self.account.id)
        self.assertTrue(invoice.bank_currency._is_PREMIUM)
        self.assertEqual(invoice.bank_amount, 5 * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR)
        self.assertEqual(invoice.user_id, self.account.email)
        self.assertTrue(invoice.comment)
        self.assertEqual(invoice.payment_amount, 5)
        self.assertTrue(invoice.payment_currency._is_USD)

        self.check_ajax_ok(response, data={'next_url': invoice.simple_payment_url})

    def test_creation_limits(self):
        for i in xrange(dengionline_settings.CREATION_NUMBER_LIMIT):
            self.check_ajax_ok(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5)))
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5)),
                              'payments.pay_with_dengionline.creation_limit_riched')

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_dengionline_disabled__global(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5)),
                              'payments.dengionline_disabled')

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', True)
    def test_dengionline_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_ajax_error(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5)),
                              'payments.dengionline_disabled')

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_dengionline_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_ajax_ok(self.post_ajax_json(url('accounts:payments:pay-with-dengionline'), self.post_data(5)))


class PayDialogRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(PayDialogRequestesTests, self).setUp()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_ajax_html(url('accounts:payments:dengionline-dialog')), texts=['common.fast_account'])

    def test_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(url('accounts:payments:dengionline-dialog')), texts=['common.login_required'])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    @mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [])
    def test_dengionline_disabled__global(self):
        self.check_html_ok(self.request_ajax_html(url('accounts:payments:dengionline-dialog')), texts=['payments.dengionline_disabled'])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', True)
    def test_dengionline_disabled__settings(self):
        del settings[payments_settings.SETTINGS_ALLOWED_KEY]
        self.check_html_ok(self.request_ajax_html(url('accounts:payments:dengionline-dialog')), texts=['payments.dengionline_disabled'])

    @mock.patch('accounts.payments.conf.payments_settings.ENABLE_REAL_PAYMENTS', False)
    def test_dengionline_disabled__global_with_exception(self):
        with mock.patch('accounts.payments.conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS', [self.account.id]):
            self.check_html_ok(self.request_ajax_html(url('accounts:payments:dengionline-dialog')), texts=[('payments.dengionline_disabled', 0)])


class GiveMoneyRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(GiveMoneyRequestesTests, self).setUp()

        result, account_id, bundle_id = register_user('superuser', 'superuser@test.com', '111111')
        self.superuser = AccountPrototype.get_by_id(account_id)
        self.superuser._model.is_superuser = True
        self.superuser.save()

        self.request_login('superuser@test.com')

    def post_data(self, amount=105):
        return {'amount': amount, 'description': u'bla-bla'}

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('accounts:payments:give-money', account=self.account.id), self.post_data()), 'payments.give_money.fast_account')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_for_wront_account(self):
        self.check_ajax_error(self.client.post(url('accounts:payments:give-money', account='xxx'), self.post_data()), 'payments.give_money.account.wrong_format')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('accounts:payments:give-money', account=self.account.id), self.post_data()), 'common.login_required')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_from_errors(self):
        self.check_ajax_error(self.client.post(url('accounts:payments:give-money', account=self.account.id), {'amount': 'x', 'description': u'bla-bla'}),
                              'payments.give_money.form_errors')
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

    def test_success(self):
        self.assertEqual(BankInvoicePrototype._db_count(), 0)
        response = self.post_ajax_json(url('accounts:payments:give-money', account=self.account.id), self.post_data(amount=5))
        self.assertEqual(BankInvoicePrototype._db_count(), 1)

        invoice = BankInvoicePrototype._db_get_object(0)

        self.assertTrue(invoice.recipient_type._is_GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertTrue(invoice.sender_type._is_GAME_MASTER)
        self.assertEqual(invoice.sender_id, self.superuser.id)
        self.assertTrue(invoice.currency._is_PREMIUM)
        self.assertEqual(invoice.amount, 5)
        self.assertEqual(invoice.description, u'bla-bla')
        self.assertTrue(invoice.state._is_FORCED)

        self.check_ajax_ok(response)


class SuccessedRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(SuccessedRequestesTests, self).setUp()

    def test_success(self):
        self.check_html_ok(self.request_html(url('accounts:payments:successed')))


class FailedRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(FailedRequestesTests, self).setUp()

    def test_success(self):
        self.check_html_ok(self.request_html(url('accounts:payments:failed')))
