# coding: utf-8

import mock

from dext.utils.urls import url

from common.utils import testcase
from common.postponed_tasks import PostponedTaskPrototype

from bank.prototypes import InvoicePrototype
from bank.tests.helpers import BankTestsMixin

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from accounts.payments.price_list import PURCHASES_BY_UID


class RequestesTestsBase(testcase.TestCase):

    def setUp(self):
        super(RequestesTestsBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.request_login(self.account.email)


class ShopRequestesTests(RequestesTestsBase):

    def setUp(self):
        super(ShopRequestesTests, self).setUp()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.client.get(url('accounts:payments:shop')), texts=['common.fast_account'])

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:payments:shop')
        self.check_redirect(requested_url, login_url(requested_url))

    @mock.patch('accounts.payments.price_list.PRICE_LIST', [])
    def test_no_goods(self):
        self.check_html_ok(self.client.get(url('accounts:payments:shop')), texts=['pgf-no-goods-message'])

    def test_goods(self):
        self.check_html_ok(self.client.get(url('accounts:payments:shop')), texts=[('pgf-no-goods-message', 0)] + PURCHASES_BY_UID.keys())


class HistoryRequestesTests(RequestesTestsBase, BankTestsMixin):

    def setUp(self):
        super(HistoryRequestesTests, self).setUp()

    def test_for_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.client.get(url('accounts:payments:history')), texts=['common.fast_account'])

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:payments:history')
        self.check_redirect(requested_url, login_url(requested_url))

    def test_no_history(self):
        self.check_html_ok(self.client.get(url('accounts:payments:history')), texts=['pgf-no-history-message'])

    def test_history(self):
        self.create_bank_account(self.account.id)
        history = self.create_entity_history(self.account.id)
        invoices = InvoicePrototype._all()

        histroy_ids = [invoice.id for invoice in history]

        texts = [('pgf-no-history-message', 0)]

        for invoice in invoices:
            if invoice.id in histroy_ids:
                continue
            texts.append((invoice.description, 0))

        for invoice in history:
            texts.append((invoice.description, 1))

        self.check_html_ok(self.client.get(url('accounts:payments:history')), texts=texts)


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
        self.check_ajax_error(self.client.post(url('accounts:payments:buy', purchase='wrong-uid')), 'payments.purchase.not_found')

    def test_success(self):
        response = self.client.post(url('accounts:payments:buy', purchase=self.purchase.uid))
        self.check_ajax_processing(response, PostponedTaskPrototype._get_object(0).status_url)
