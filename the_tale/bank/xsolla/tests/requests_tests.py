# coding: utf-8
import mock

from dext.utils.urls import url

from common.utils import testcase

from bank.xsolla.logic import check_user_md5, pay_md5, cancel_md5
from bank.xsolla.relations import COMMAND_TYPE, CHECK_USER_RESULT, COMMON_RESULT, PAY_RESULT, CANCEL_RESULT
from bank.xsolla.prototypes import InvoicePrototype


class BaseRequestsTests(testcase.TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()
        self.user_email = 'test@mailinator.com'
        self.check_user_md5 = check_user_md5(command=COMMAND_TYPE.CHECK, v1=self.user_email)


    def construct_url(self, command, md5_hash='', **kwargs):
        v1 = kwargs.get('v1', self.user_email)

        if 'v1' in kwargs:
            del kwargs['v1']

        return url('bank:xsolla:command',
                   command=command.value,
                   v1=v1,
                   md5=md5_hash,
                   **kwargs)


    def construct_answer(self, check_result):
        answer = u'''<?xml version="1.0" encoding="windows-1251"?>
<response>
    <result>%(xsolla_result)s</result>
    <comment>%(comment)s</comment>
</response>
''' % {'xsolla_result': check_result.xsolla_result.value, 'comment': check_result.text}

        return answer



class CommonRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CommonRequestsTests, self).setUp()

    def test_wrong_ips(self):
        with mock.patch('bank.xsolla.conf.xsolla_settings.ALLOWED_IPS', ()):
            self.check_xml_ok(self.request_xml(self.construct_url(command=COMMAND_TYPE.CHECK)),
                              body=self.construct_answer(COMMON_RESULT.DISALLOWED_IP),
                              encoding='cp1251')


    def test_wrong_command(self):
        self.check_xml_ok(self.request_xml(url('bank:xsolla:command', command='wrong-command')),
                          body=self.construct_answer(COMMON_RESULT.WRONG_COMMAND),
                          encoding='cp1251')

    @mock.patch('bank.xsolla.views.logger.error', mock.Mock())
    def test_exception_raised(self):
        def raise_exception(*argv, **kwargs):
            raise Exception('!')

        with mock.patch('bank.xsolla.logic.check_user', raise_exception):
            self.check_xml_ok(self.request_xml(self.construct_url(command=COMMAND_TYPE.CHECK)),
                              body=self.construct_answer(COMMON_RESULT.UNKNOWN_ERROR),
                              encoding='cp1251')



class CheckUserRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CheckUserRequestsTests, self).setUp()

    def construct_url(self, md5_hash=None, **kwargs):
        return super(CheckUserRequestsTests, self).construct_url(command=COMMAND_TYPE.CHECK,
                                                                 md5_hash=md5_hash if md5_hash else self.check_user_md5,
                                                                 **kwargs)

    def test_check_user__wrong_md5(self):
        self.check_xml_ok(self.request_xml(self.construct_url(md5_hash='bla-bla')),
                          body=self.construct_answer(CHECK_USER_RESULT.WRONG_MD5),
                          encoding='cp1251')

    def test_check_user__user_exists(self):
        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=13)) as bank_check_user:
            self.check_xml_ok(self.request_xml(self.construct_url()),
                              body=self.construct_answer(CHECK_USER_RESULT.USER_EXISTS),
                              encoding='cp1251')

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))


    def test_check_user__user_not_exists(self):
        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=None)) as bank_check_user:
            self.check_xml_ok(self.request_xml(self.construct_url()),
                              body=self.construct_answer(CHECK_USER_RESULT.USER_NOT_EXISTS),
                              encoding='cp1251')

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))


class PayRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(PayRequestsTests, self).setUp()
        self.user_email = 'test@mailinator.com'
        self.xsolla_id = '666'
        self.payment_sum = '13'
        self.pay_md5 = pay_md5(command=COMMAND_TYPE.PAY, v1=self.user_email, id=self.xsolla_id)

    def construct_url(self, **kwargs):
        md5_hash = kwargs.get('md5_hash', self.pay_md5)
        v1 = kwargs.get('v1', self.user_email)
        xsolla_id = kwargs.get('xsolla_id', self.xsolla_id)
        payment_sum = kwargs.get('payment_sum', self.payment_sum)
        return super(PayRequestsTests, self).construct_url(command=COMMAND_TYPE.PAY,
                                                           md5_hash=md5_hash,
                                                           v1=v1,
                                                           id=xsolla_id,
                                                           sum=payment_sum)

    def construct_pay_answer(self, pay_result, internal_id, **kwargs):
        xsolla_id = kwargs.get('xsolla_id', self.xsolla_id)
        payment_sum = kwargs.get('payment_sum', self.payment_sum)
        answer = u'''<?xml version="1.0" encoding="windows-1251"?>
<response>
    <id>%(xsolla_id)s</id>
    <id_shop>%(internal_id)s</id_shop>
    <sum>%(sum)s</sum>
    <result>%(xsolla_result)s</result>
    <comment>%(comment)s</comment>
</response>
''' % {'xsolla_result': pay_result.xsolla_result.value,
       'comment': pay_result.text,
       'xsolla_id': xsolla_id,
       'internal_id': internal_id,
       'sum': payment_sum}

        return answer


    def test_wrong_md5(self):
        self.check_xml_ok(self.request_xml(self.construct_url(md5_hash='bla-bla')),
                          body=self.construct_pay_answer(PAY_RESULT.WRONG_MD5, internal_id=None),
                          encoding='cp1251')

    def test_success(self):
        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=13)) as bank_check_user:
            response = self.request_xml(self.construct_url())

        self.check_xml_ok(response,
                          body=self.construct_pay_answer(PAY_RESULT.SUCCESS, internal_id=InvoicePrototype._db_get_object(0).id),
                          encoding='cp1251')

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))


    def test_user_not_exists(self):
        with mock.patch('bank.logic.get_account_id', mock.Mock(return_value=None)) as bank_check_user:
            response = self.request_xml(self.construct_url())

        self.check_xml_ok(response,
                          body=self.construct_pay_answer(PAY_RESULT.USER_NOT_EXISTS, internal_id=InvoicePrototype._db_get_object(0).id),
                          encoding='cp1251')

        self.assertEqual(bank_check_user.call_count, 1)
        self.assertEqual(bank_check_user.call_args, mock.call(email=self.user_email))


class CancelRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CancelRequestsTests, self).setUp()
        self.xsolla_id = '666'
        self.cancel_md5 = cancel_md5(command=COMMAND_TYPE.CANCEL, id=self.xsolla_id)

    def construct_url(self, md5_hash=None, **kwargs):
        return super(CancelRequestsTests, self).construct_url(command=COMMAND_TYPE.CANCEL,
                                                              md5_hash=md5_hash if md5_hash else self.cancel_md5,
                                                              **kwargs)

    def test_not_supported(self):
        self.check_xml_ok(self.request_xml(self.construct_url()),
                          body=self.construct_answer(CANCEL_RESULT.NOT_SUPPORTED),
                          encoding='cp1251')
