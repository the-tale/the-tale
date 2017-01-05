# coding: utf-8
from unittest import mock
import random

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.map.conf import map_settings

from ..models import Building
from .. import logic
from ..prototypes import ResourceExchangePrototype
from .. import storage
from ..relations import RESOURCE_EXCHANGE_TYPE


class ResourceExchangeTests(testcase.TestCase):

    def setUp(self):
        super(ResourceExchangeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
        self.resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE.records)

        self.exchange = ResourceExchangePrototype.create(place_1=self.place_1,
                                                         place_2=self.place_2,
                                                         resource_1=self.resource_1,
                                                         resource_2=self.resource_2,
                                                         bill=None)

    def test_create(self):
        self.assertEqual(self.exchange.place_1.id, self.place_1.id)
        self.assertEqual(self.exchange.place_2.id, self.place_2.id)
        self.assertEqual(self.exchange.resource_1, self.resource_1)
        self.assertEqual(self.exchange.resource_2, self.resource_2)
        self.assertEqual(self.exchange.bill_id, None)

    def test_get_resources_for_place__place_1(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_1),
                         (self.resource_1, self.resource_2, self.place_2))

    def test_get_resources_for_place__place_2(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_2),
                         (self.resource_2, self.resource_1, self.place_1))


    def test_get_resources_for_place__wrong_place(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_3),
                         (RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE, None))
