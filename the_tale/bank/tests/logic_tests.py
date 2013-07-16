# coding: utf-8

from common.utils import testcase

from bank import logic


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

    def test_get_account_id_function_defined(self):
        self.assertTrue(callable(logic._GET_ACCOUNT_ID_BY_EMAIL_FUNCTION))
