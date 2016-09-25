# coding: utf-8

import datetime

import mock

from the_tale.common.utils import testcase

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations
from the_tale.statistics.tests.helpers import TestMetric
from the_tale.statistics.metrics import exceptions as metrics_exceptions


class BaseMetricsTests(testcase.TestCase):

    def setUp(self):
        super(BaseMetricsTests, self).setUp()
        self.date = datetime.datetime.now()
        self.metric = TestMetric()
        self.metric.initialize()

    @mock.patch('the_tale.statistics.metrics.base.BaseMetric._last_datetime', lambda self: datetime.datetime(year=6, month=6, day=6, hour=6))
    def test_initialize(self):
        self.metric.initialize()
        self.assertEqual(self.metric.last_datetime, datetime.datetime(year=6, month=6, day=6, hour=6))
        self.assertEqual(self.metric.last_date, datetime.date(year=6, month=6, day=6))
        self.assertEqual(self.metric.free_date, datetime.date(year=6, month=6, day=7))
        self.assertEqual(self.metric.now_date, datetime.datetime.now().date() - datetime.timedelta(days=1))

    def test_last_datetime__no_records(self):
        self.assertEqual(RecordPrototype._db_filter(type=TestMetric.TYPE).count(), 0)
        self.assertEqual(self.metric._last_datetime(), datetime.datetime(year=2012, month=6, day=26))

    def test_last_datetime__has_records(self):
        self.metric.store_value(datetime.datetime(year=6, month=6, day=6, hour=6), 1)
        self.assertEqual(self.metric._last_datetime(), datetime.datetime(year=6, month=6, day=6, hour=6))

    def test_store_value__int(self):
        self.metric.store_value(datetime.datetime(year=6, month=6, day=6, hour=6), 666)
        self.assertEqual(RecordPrototype._db_filter(type=TestMetric.TYPE).count(), 1)
        record = RecordPrototype._db_get_object(0)
        self.assertEqual(record.date, datetime.datetime(year=6, month=6, day=6, hour=6))
        self.assertEqual(record.value_int, 666)
        self.assertEqual(record.value_float, 666.0)
        self.assertTrue(record.type.is_TEST_INT)

    @mock.patch('the_tale.statistics.tests.helpers.TestMetric.TYPE', relations.RECORD_TYPE.TEST_FLOAT)
    def test_store_value__float(self):
        self.metric.store_value(datetime.datetime(year=6, month=6, day=6, hour=6), 666.6)
        self.assertEqual(RecordPrototype._db_filter(type=TestMetric.TYPE).count(), 1)
        record = RecordPrototype._db_get_object(0)
        self.assertEqual(record.date, datetime.datetime(year=6, month=6, day=6, hour=6))
        self.assertEqual(record.value_int, 666)
        self.assertEqual(record.value_float, 666.6)
        self.assertTrue(record.type.is_TEST_FLOAT)

    @mock.patch('the_tale.statistics.metrics.base.BaseMetric._last_datetime', lambda self: datetime.datetime(year=6, month=6, day=6, hour=6))
    def test_get_interval(self):
        self.metric.initialize()
        self.assertEqual(self.metric._get_interval(),
                         (datetime.date(year=6, month=6, day=7), datetime.datetime.now().date()))

    @mock.patch('the_tale.statistics.metrics.base.BaseMetric._get_interval',
                lambda self: (datetime.datetime(year=6, month=6, day=6, hour=6), datetime.datetime(year=6, month=6, day=9, hour=6)))
    def test_complete_values(self):
        with mock.patch('the_tale.statistics.metrics.base.BaseMetric.store_value') as store_value:
            self.metric.complete_values()

        self.assertEqual(store_value.call_args_list,
                         [mock.call(datetime.date(year=6, month=6, day=6), 1),
                          mock.call(datetime.date(year=6, month=6, day=7), 2),
                          mock.call(datetime.date(year=6, month=6, day=8), 3)])

    def test_complete_values__block_second_time(self):
        self.metric.complete_values()
        self.assertRaises(metrics_exceptions.ValuesCompletedError, self.metric.complete_values)

    def test_no_second_record(self):
        self.metric.complete_values()
        self.assertTrue(RecordPrototype._db_count() > 0)

        self.metric.initialize()

        with self.check_not_changed(RecordPrototype._db_count):
            self.metric.complete_values()

    def test_db_date_gt(self):
        self.assertEqual(self.metric.db_date_gt('x').children, [('x__gt', self.metric.free_date + datetime.timedelta(days=1))])

    def test_db_date_gt__with_date(self):
        self.assertEqual(self.metric.db_date_gt('x', date=self.date).children, [('x__gt', self.date + datetime.timedelta(days=1))])

    def test_db_date_gte(self):
        self.assertEqual(self.metric.db_date_gte('x').children, [('x__gt', self.metric.free_date)])

    def test_db_date_gte__with_date(self):
        self.assertEqual(self.metric.db_date_gte('x', date=self.date).children, [('x__gt', self.date)])

    def test_db_date_lt(self):
        self.assertEqual(self.metric.db_date_lt('x').children, [('x__lt', self.metric.free_date)])

    def test_db_date_lt__with_date(self):
        self.assertEqual(self.metric.db_date_lt('x', date=self.date).children, [('x__lt', self.date)])

    def test_db_date_lte(self):
        self.assertEqual(self.metric.db_date_lte('x').children, [('x__lt', self.metric.free_date + datetime.timedelta(days=1))])

    def test_db_date_lte__with_date(self):
        self.assertEqual(self.metric.db_date_lte('x', date=self.date).children, [('x__lt', self.date + datetime.timedelta(days=1))])

    def test_db_date_interval(self):
        self.assertEqual(self.metric.db_date_interval('x', days=10).children,
                         [('x__gt', self.metric.free_date), ('x__lt', self.metric.free_date + datetime.timedelta(days=10))])
        self.assertEqual(self.metric.db_date_interval('x', days=-10).children,
                         [('x__lt', self.metric.free_date +  + datetime.timedelta(days=1)), ('x__gt', self.metric.free_date + datetime.timedelta(days=-9))])
        self.assertEqual(self.metric.db_date_interval('x', days=0).children,
                         [('x__gt', self.metric.free_date), ('x__lt', self.metric.free_date + datetime.timedelta(days=1))])

    def test_db_date_interval__with_date(self):
        self.assertEqual(self.metric.db_date_interval('x', days=10, date=self.date).children,
                         [('x__gt', self.date), ('x__lt', self.date + datetime.timedelta(days=10))])
        self.assertEqual(self.metric.db_date_interval('x', days=-10, date=self.date).children,
                         [('x__lt', self.date +  + datetime.timedelta(days=1)), ('x__gt', self.date + datetime.timedelta(days=-9))])
        self.assertEqual(self.metric.db_date_interval('x', days=0, date=self.date).children,
                         [('x__gt', self.date), ('x__lt', self.date + datetime.timedelta(days=1))])

    def test_db_date_day(self):
        with mock.patch('the_tale.statistics.metrics.base.BaseMetric.db_date_interval') as db_date_interval:
            self.metric.db_date_day('x')
        self.assertEqual(db_date_interval.call_args_list, [mock.call('x', date=self.metric.free_date, days=0)])

    def test_db_date_day__with_date(self):
        with mock.patch('the_tale.statistics.metrics.base.BaseMetric.db_date_interval') as db_date_interval:
            self.metric.db_date_day('x', date=self.date)
        self.assertEqual(db_date_interval.call_args_list, [mock.call('x', date=self.date, days=0)])
