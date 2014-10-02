# coding: utf-8

import random

from the_tale.game.map.places.relations import RESOURCE_EXCHANGE_TYPE

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.bills.conf import bills_settings

from the_tale.game.bills.bills.place_resource_exchange import ALLOWED_EXCHANGE_TYPES
from the_tale.game.bills.bills.place_resource_conversion import CONVERSION


class BaseTestPrototypes(TestCase):

    def setUp(self):
        super(BaseTestPrototypes, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4', 'test_user4@test.com', '111111')
        self.account4 = AccountPrototype.get_by_id(account_id)

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
