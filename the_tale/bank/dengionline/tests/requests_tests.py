# coding: utf-8

from dext.utils.urls import url

from common.utils import testcase

from bank.dengionline.relations import CHECK_USER_RESULT, INVOICE_STATE
from bank.dengionline.prototypes import InvoicePrototype

from bank.dengionline.tests.helpers import TestInvoiceFabric


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
