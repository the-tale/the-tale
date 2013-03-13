# coding: utf-8

import os

from common.utils.testcase import TestCase
from common.utils import xls

class XLSTests(TestCase):

    def setUp(self):
        super(XLSTests, self).setUp()

    def test_load_table_simple(self):
        data = xls.load_table(os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=0)
        self.assertEqual(data, [ [3.0,   u'd', 3.0,  4.0,  '',    ''],
                                 ['',    2.0,  3.0,  4.0,  u'df', u'+'],
                                 ['',    6.0,  7.0,  8.0,  '',    ''],
                                 [123.0, 23.0, 34.0, 45.0, u'qw', '']])

    def test_load_table_with_rows(self):
        data = xls.load_table(os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=1,
                              rows=[u'row1', u'row2', u'row3', u'row4'])
        self.assertEqual(data,
                         {'row1': [3.0,   u'd', 3.0,  4.0,  '',    ''],
                          'row2': ['',    2.0,  3.0,  4.0,  u'df', u'+'],
                          'row3': ['',    6.0,  7.0,  8.0,  '',    ''],
                          'row4': [123.0, 23.0, 34.0, 45.0, u'qw', '']})

    def test_load_table_with_rows_duplicate_rows_in_args(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=1,
                          rows=[u'row1', u'row2', u'row2', u'row4'])

    def test_load_table_with_rows_duplicate_rows(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=2,
                          rows=[u'row1', u'row2', u'row3', u'row4'])


    def test_load_table_with_rows_undefined_rows(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=2,
                          rows=[u'row1', u'row2', u'row3', u'row5'])

    def test_load_table_with_columns(self):
        data = xls.load_table(os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=3,
                              columns=['col1', 'col2', 'col3', 'col4', 'col5'])

        self.assertEqual(data, [ {'col1': 3.0,   'col2': u'd', 'col3': 3.0,  'col4': 4.0,  'col5': ''},
                                 {'col1': '',    'col2': 2.0,  'col3': 3.0,  'col4': 4.0,  'col5': u'df'},
                                 {'col1': '',    'col2': 6.0,  'col3': 7.0,  'col4': 8.0,  'col5': ''},
                                 {'col1': 123.0, 'col2': 23.0, 'col3': 34.0, 'col4': 45.0, 'col5': u'qw'}])

    def test_load_table_with_columns_duplicate_column_in_args(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=3,
                          columns=['col1', 'col2', 'col2', 'col4', 'col5'])

    def test_load_table_with_columns_duplicate_column(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=4,
                          columns=['col1', 'col2', 'col3', 'col4', 'col5'])

    def test_load_table_with_columns_too_long_columns(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=5,
                          columns=['col1', 'col2', 'col3', 'col4', 'col5'])

    def test_load_table_with_rows_and_columns(self):
        data = xls.load_table(os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=6,
                              rows=[u'row1', u'row2', u'row3', u'row4'],
                              columns=['col1', 'col2', 'col3', 'col4', 'col5'])

        self.assertEqual(data, { 'row1': {'col1': 3.0,   'col2': u'd', 'col3': 3.0,  'col4': 4.0,  'col5': ''},
                                 'row2': {'col1': '',    'col2': 2.0,  'col3': 3.0,  'col4': 4.0,  'col5': u'df'},
                                 'row3': {'col1': '',    'col2': 6.0,  'col3': 7.0,  'col4': 8.0,  'col5': ''},
                                 'row4': {'col1': 123.0, 'col2': 23.0, 'col3': 34.0, 'col4': 45.0, 'col5': u'qw'} })

    def test_load_table_with_rows_and_columns_undefined_row(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=6,
                          rows=[u'row1', u'row2', u'row3', u'row5'],
                          columns=['col1', 'col2', 'col3', 'col4', 'col5'])

    def test_load_table_with_rows_and_columns_undefined_column(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=6,
                          rows=[u'row1', u'row2', u'row3', u'row5'],
                          columns=['col1', 'col2', 'col6', 'col4', 'col5'])

    def test_load_table_with_rows_and_columns_duplicate_row(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=7,
                          rows=[u'row1', u'row2', u'row3', u'row4'],
                          columns=['col1', 'col2', 'col3', 'col4', 'col5'])

    def test_load_table_with_rows_and_columns_duplicate_column(self):
        self.assertRaises(xls.XLSException,
                          xls.load_table, os.path.join(os.path.dirname(__file__), 'fixtures/xls_table_simple.xls'), sheet_index=8,
                          rows=[u'row1', u'row2', u'row3', u'row4'],
                          columns=['col1', 'col2', 'col3', 'col4', 'col5'])
