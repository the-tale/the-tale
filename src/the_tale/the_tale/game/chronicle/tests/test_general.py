
import smart_imports

smart_imports.all()


class GeneralTests(utils_testcase.TestCase):

    def setUp(self):
        super(GeneralTests, self).setUp()

    def test_every_bill_has_argument_getter(self):
        self.assertCountEqual(list(signal_processors.BILL_ARGUMENT_GETTERS.keys()),
                              bills_relations.BILL_TYPE.records)
