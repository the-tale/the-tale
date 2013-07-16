# coding: utf-8

import mock

from bank.xsolla.prototypes import InvoicePrototype


class TestInvoiceFabric(object):

    def __init__(self):
        self.user_email = 'test@mailinator.com'
        self.xsolla_id = '1'
        self.payment_sum = '101'
        self.account_id = 666
        self._test = None
        self.v2 = 'bla-bla'
        self.v3 = 'alb-alb'


    def create_invoice(self, **kwargs):
        if set(kwargs.keys()) - set(['account_id', 'user_email', 'xsolla_id', 'payment_sum', 'test']):
            raise Exception('wrong agruments in create_invoice')

        account_id = kwargs.get('account_id', self.account_id)
        user_email = kwargs.get('user_email', self.user_email)
        xsolla_id = kwargs.get('xsolla_id', self.xsolla_id)
        payment_sum = kwargs.get('payment_sum', self.payment_sum)
        test = kwargs.get('test', self._test)

        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=account_id)):
            return InvoicePrototype.create(v1=user_email,
                                           v2=self.v2,
                                           v3=self.v3,
                                           xsolla_id=xsolla_id,
                                           payment_sum=payment_sum,
                                           test=test)


    def pay(self, **kwargs):
        if set(kwargs.keys()) - set(['account_id', 'user_email', 'xsolla_id', 'payment_sum', 'test']):
            raise Exception('wrong agruments in pay')

        account_id = kwargs.get('account_id', self.account_id)
        user_email = kwargs.get('user_email', self.user_email)
        xsolla_id = kwargs.get('xsolla_id', self.xsolla_id)
        payment_sum = kwargs.get('payment_sum', self.payment_sum)
        test = kwargs.get('test', self._test)

        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=account_id)):
            return InvoicePrototype.pay(v1=user_email,
                                        v2=self.v2,
                                        v3=self.v3,
                                        xsolla_id=xsolla_id,
                                        payment_sum=payment_sum,
                                        test=test)
