# coding: utf-8

import datetime

from the_tale.common.utils import testcase

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations
from the_tale.statistics import exceptions


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        self.date = datetime.datetime.now()
        self.timedelta = datetime.timedelta(microseconds=1)

    def test_create(self):

        with self.check_delta(RecordPrototype._db_count, 1):
            record = RecordPrototype.create(type=relations.RECORD_TYPE.TEST_INT,
                                            date=self.date,
                                            value_int=666, value_float=666.6)

        record.reload()

        self.assertTrue(record.type.is_TEST_INT)
        self.assertEqual(record.date, self.date)
        self.assertEqual(record.value_int, 666)
        self.assertEqual(record.value_float, 666.6)

    def test_create__values_not_specified(self):
        self.assertRaises(exceptions.ValueNotSpecifiedError, RecordPrototype.create, type=relations.RECORD_TYPE.TEST_INT, date=self.date)

    def test_create__values_not_specified_for_type(self):
        self.assertRaises(exceptions.ValueNotSpecifiedForTypeError, RecordPrototype.create, type=relations.RECORD_TYPE.TEST_INT, date=self.date, value_float=6.66)
        self.assertRaises(exceptions.ValueNotSpecifiedForTypeError, RecordPrototype.create, type=relations.RECORD_TYPE.TEST_FLOAT, date=self.date, value_int=666)

    def test_create__int_specified(self):
        record = RecordPrototype.create(type=relations.RECORD_TYPE.TEST_FLOAT, date=self.date, value_float=666.6)

        record.reload()

        self.assertEqual(record.value_int, 666)

    def test_create__float_specified(self):
        record = RecordPrototype.create(type=relations.RECORD_TYPE.TEST_INT, date=self.date, value_int=666)

        record.reload()

        self.assertEqual(record.value_float, 666.0)

    def test_select__inverted_interval(self):
        date_1 = self.date
        date_2 = self.date + self.timedelta
        self.assertRaises(exceptions.InvertedDateIntervalError, RecordPrototype.select, type=relations.RECORD_TYPE.TEST_INT, date_from=date_2, date_to=date_1)

    def test_select__int(self):
        dates = [self.date + self.timedelta * i for i in range(4)]

        RecordPrototype.create(type=relations.RECORD_TYPE.TEST_INT, date=dates[1], value_int=417)
        RecordPrototype.create(type=relations.RECORD_TYPE.TEST_INT, date=dates[2], value_int=666)

        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_INT, date_from=dates[0], date_to=dates[3]), [(dates[1], 417), (dates[2], 666)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_INT, date_from=dates[1], date_to=dates[2]), [(dates[1], 417), (dates[2], 666)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_INT, date_from=dates[1], date_to=dates[1]), [(dates[1], 417)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_INT, date_from=dates[2], date_to=dates[2]), [(dates[2], 666)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_INT, date_from=dates[3], date_to=dates[3]), [])

    def test_select__float(self):
        dates = [self.date + self.timedelta * i for i in range(4)]

        RecordPrototype.create(type=relations.RECORD_TYPE.TEST_FLOAT, date=dates[1], value_float=41.7)
        RecordPrototype.create(type=relations.RECORD_TYPE.TEST_FLOAT, date=dates[2], value_float=66.6)

        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_FLOAT, date_from=dates[0], date_to=dates[3]), [(dates[1], 41.7), (dates[2], 66.6)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_FLOAT, date_from=dates[1], date_to=dates[2]), [(dates[1], 41.7), (dates[2], 66.6)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_FLOAT, date_from=dates[1], date_to=dates[1]), [(dates[1], 41.7)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_FLOAT, date_from=dates[2], date_to=dates[2]), [(dates[2], 66.6)])
        self.assertEqual(RecordPrototype.select(type=relations.RECORD_TYPE.TEST_FLOAT, date_from=dates[3], date_to=dates[3]), [])

    def test_remove_by_type(self):
        RecordPrototype.create(type=relations.RECORD_TYPE.TEST_INT, date=self.date, value_int=41.7)
        record = RecordPrototype.create(type=relations.RECORD_TYPE.TEST_FLOAT, date=self.date, value_float=66.6)

        RecordPrototype.remove_by_type(relations.RECORD_TYPE.TEST_INT)

        self.assertEqual(list(RecordPrototype._db_all().values_list('id', flat=True)), [record.id])
