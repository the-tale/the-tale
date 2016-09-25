# coding: utf-8

from the_tale.game.bills import relations as bills_relations
from the_tale.game.bills.tests.test_prototype import BaseTestPrototypes

from the_tale.game.chronicle import signal_processors


class GeneralTests(BaseTestPrototypes):

    def setUp(self):
        super(GeneralTests, self).setUp()


    def test_every_bill_has_argument_getter(self):
        self.assertItemsEqual(signal_processors.BILL_ARGUMENT_GETTERS.keys(),
                              bills_relations.BILL_TYPE.records)
