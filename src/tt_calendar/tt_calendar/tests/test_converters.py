
import unittest

from .. import datetime
from .. import converters


class ComverterV1Tests(unittest.TestCase):

    def test_from_turns(self):
        converter = converters.ConverterV1()

        self.assertEqual(converter.from_turns(0), datetime.DateTime(year=0, month=0, day=0, hour=0, minute=0, second=0))
        self.assertEqual(converter.from_turns(1000000), datetime.DateTime(year=12, month=1, day=51, hour=21, minute=20, second=0))

    def test_from_seconds(self):
        converter = converters.ConverterV1()

        self.assertEqual(converter.from_seconds(0), datetime.DateTime(year=0, month=0, day=0, hour=0, minute=0, second=0))
        self.assertEqual(converter.from_seconds(1000000), datetime.DateTime(year=0, month=0, day=35, hour=13, minute=46, second=40))


class ComverterV2Tests(unittest.TestCase):

    def test_from_turns___before_barrier(self):
        converter = converters.ConverterV2()

        self.assertEqual(converter.from_turns(0), datetime.DateTime(year=0, month=0, day=0, hour=0, minute=0, second=0))
        self.assertEqual(converter.from_turns(1000000), datetime.DateTime(year=12, month=1, day=51, hour=21, minute=20, second=0))

    def test_from_turns__on_barrier(self):
        converter = converters.ConverterV2()

        self.assertEqual(converter.from_turns(converter.TURNS_BARRIER - 1),
                         datetime.DateTime(year=206, month=0, day=35, hour=7, minute=58, second=0))

        self.assertEqual(converter.from_turns(converter.TURNS_BARRIER),
                         datetime.DateTime(year=206, month=0, day=35, hour=8, minute=0, second=0))

        self.assertEqual(converter.from_turns(converter.TURNS_BARRIER + 1),
                         datetime.DateTime(year=206, month=0, day=35, hour=8, minute=1, second=0))

    def test_from_turns__after_barrier(self):
        converter = converters.ConverterV2()

        self.assertEqual(converter.from_turns(converter.TURNS_BARRIER*10),
                         datetime.DateTime(year=494, month=2, day=50, hour=8, minute=0, second=0))

    def test_from_seconds(self):
        converter = converters.ConverterV2()

        self.assertEqual(converter.from_seconds(0), datetime.DateTime(year=0, month=0, day=0, hour=0, minute=0, second=0))
        self.assertEqual(converter.from_seconds(1000000), datetime.DateTime(year=0, month=0, day=11, hour=13, minute=46, second=40))
