# coding: utf-8

import random

from the_tale.game.places.relations import RESOURCE_EXCHANGE_TYPE

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.bills.conf import bills_settings

from the_tale.game.bills.bills.place_resource_exchange import ALLOWED_EXCHANGE_TYPES
from the_tale.game.bills.bills.place_resource_conversion import CONVERSION


class BaseTestPrototypes(TestCase):

    def setUp(self):
        super(BaseTestPrototypes, self).setUp()

        self.place1, self.place2, self.place3 = create_test_map()

        self.account1 = self.accounts_factory.create_account()
        self.account2 = self.accounts_factory.create_account()
        self.account3 = self.accounts_factory.create_account()
        self.account4 = self.accounts_factory.create_account()

        from the_tale.forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)


def choose_exchange_resources():
    resource_1, resource_2 = RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE
    while resource_1.parameter == resource_2.parameter:
        resource_1 = random.choice(ALLOWED_EXCHANGE_TYPES)
        resource_2 = random.choice(ALLOWED_EXCHANGE_TYPES)
    return resource_1, resource_2


def choose_conversions():
    conversion_1, conversion_2 = None, None
    while conversion_1 == conversion_2:
        conversion_1 = random.choice(CONVERSION.records)
        conversion_2 = random.choice(CONVERSION.records)
    return conversion_1, conversion_2
