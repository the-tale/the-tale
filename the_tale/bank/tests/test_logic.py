# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.bank import logic


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

    def test_get_account_id_function_defined(self):
        self.assertTrue(callable(logic._GET_ACCOUNT_ID_BY_EMAIL_FUNCTION))
