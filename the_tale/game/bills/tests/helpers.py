# coding: utf-8

import random

from the_tale.game.map.places.relations import RESOURCE_EXCHANGE_TYPE

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.bills.conf import bills_settings


class BaseTestPrototypes(TestCase):

    NAME_FORMS = (u'new_name_1',
                  u'new_name_2',
                  u'new_name_3',
                  u'new_name_4',
                  u'new_name_5',
                  u'new_name_6',
                  u'new_name_7',
                  u'new_name_8',
                  u'new_name_9',
                  u'new_name_10',
                  u'new_name_11',
                  u'new_name_12')


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


def choose_resources():
    resource_1, resource_2 = RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE
    while resource_1.parameter == resource_2.parameter:
        resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
        resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
    return resource_1, resource_2
