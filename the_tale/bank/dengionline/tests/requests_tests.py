# coding: utf-8
import mock

from dext.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.bank.dengionline.relations import CHECK_USER_RESULT, INVOICE_STATE, CONFIRM_PAYMENT_RESULT
from the_tale.bank.dengionline.prototypes import InvoicePrototype

from the_tale.bank.dengionline.tests.helpers import TestInvoiceFabric

def exception_producer(*argv, **kwargs):
    raise Exception


class RequestsTestsBase(testcase.TestCase):

    def setUp(self):
        super(RequestsTestsBase, self).setUp()

        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.create_invoice()


class CheckUserRequestsTests(RequestsTestsBase):

    def construct_user_answer(self, check_result):
        return u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'answer': check_result.answer, 'comment': check_result.text}

    def test_wrong_key(self):
        self.check_xml_ok(self.post_xml(url('bank:dengionline:check-user',
                                            userid=self.invoice.user_id,
                                            key='bla-bla-key')),
                          body=self.construct_user_answer(CHECK_USER_RESULT.WRONG_KEY))

    def test_user_exists(self):
        self.check_xml_ok(self.post_xml(url('bank:dengionline:check-user',
                                                userid=self.invoice.user_id,
                                                key=InvoicePrototype.check_user_request_key(self.invoice.user_id))),
                           body=self.construct_user_answer(CHECK_USER_RESULT.USER_EXISTS))

    def test_user_not_exists(self):
        for state in INVOICE_STATE._records:
            if state._is_REQUESTED:
                continue
            self.invoice._model.state = state
            self.invoice.save()
            self.check_xml_ok(self.post_xml(url('bank:dengionline:check-user',
                                                    userid=self.invoice.user_id,
                                                    key=InvoicePrototype.check_user_request_key(self.invoice.user_id))),
                                                    body=self.construct_user_answer(CHECK_USER_RESULT.USER_NOT_EXISTS))


class ConfirmPaymentRequestsTests(RequestsTestsBase):

    def construct_user_answer(self, order_id, confirm_result):
        return u'''<?xml version="1.0" encoding="UTF-8"?>
<result>
<id>%(order_id)d</id>
<code>%(answer)s</code>
<comment>%(comment)s</comment>
</result>''' % {'order_id': order_id, 'answer': confirm_result.answer, 'comment': confirm_result.text}


    def confirm_url(self, amount=None, userid=None, paymentid=None, key=None, paymode=None, orderid=None):
        if amount is None:
            amount = self.fabric.received_amount
        if userid is None:
            userid = u'%s' % self.fabric.user_id.encode('cp1251')
        if paymentid is None:
            paymentid = self.fabric.payment_id
        if key is None:
            key = InvoicePrototype.confirm_request_key(amount=amount, user_id=userid, payment_id=paymentid)
        if paymode is None:
            paymode = self.fabric.paymode
        if orderid is None:
            orderid = self.invoice.id

        return url('bank:dengionline:confirm-payment',
                   amount=amount,
                   userid=userid,
                   paymentid=paymentid,
                   key=key,
                   paymode=paymode,
                   orderid=orderid)

    def test_confim__wrong_order_id(self):
        self.check_xml_ok(self.post_xml(self.confirm_url(orderid=666)),
                          body=self.construct_user_answer(666, CONFIRM_PAYMENT_RESULT.INVOICE_NOT_FOUND))

    def test_confim__wrong_user_id(self):
        self.check_xml_ok(self.post_xml(self.confirm_url(userid='bla-bla@bla.bla')),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.WRONG_USER_ID))

    def test_confim__key(self):
        self.check_xml_ok(self.post_xml(self.confirm_url(key='bla-bla')),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.WRONG_HASH_KEY))

    def test_confim__success(self):
        self.check_xml_ok(self.post_xml(self.confirm_url()),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.CONFIRMED))

    def test_confim__already_confirmed(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.check_xml_ok(self.post_xml(self.confirm_url()),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.ALREADY_CONFIRMED))

    def test_confim__already_confirmed__wrong_arguments(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.check_xml_ok(self.post_xml(self.confirm_url(paymode=self.fabric.paymode+1)),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.ALREADY_CONFIRMED_WRONG_ARGUMENTS))

    def test_confim__already_processed(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.invoice._model.state = INVOICE_STATE.PROCESSED
        self.invoice.save()
        self.check_xml_ok(self.post_xml(self.confirm_url()),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.ALREADY_PROCESSED))

    def test_confim__already_processed__wrong_arguments(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.invoice._model.state = INVOICE_STATE.PROCESSED
        self.invoice.save()
        self.check_xml_ok(self.post_xml(self.confirm_url(paymode=self.fabric.paymode+1)),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.ALREADY_PROCESSED_WRONG_ARGUMENTS))

    def test_confim__discarded(self):
        self.invoice._model.state = INVOICE_STATE.DISCARDED
        self.invoice.save()
        self.check_xml_ok(self.post_xml(self.confirm_url()),
                          body=self.construct_user_answer(self.invoice.id, CONFIRM_PAYMENT_RESULT.DISCARDED))

    def test_confirm__all_states_processed_correctly(self):
        for state in INVOICE_STATE._records:
            self.invoice._model.state = state
            self.invoice.save()
            self.check_xml_ok(self.post_xml(self.confirm_url()))

    @mock.patch('the_tale.bank.dengionline.prototypes.InvoicePrototype.confirm', exception_producer)
    def test_confirm_payment__exception_when_confirm(self):
        self.assertRaises(Exception, self.post_xml, self.confirm_url())
        self.invoice.reload()
        self.assertTrue(self.invoice.state._is_REQUESTED)
