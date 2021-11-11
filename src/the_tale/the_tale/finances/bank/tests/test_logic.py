
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

    def test_get_account_id_function_defined(self):
        self.assertTrue(isinstance(logic._GET_ACCOUNT_ID_BY_EMAIL_FUNCTION, collections.abc.Callable))
