
import smart_imports

smart_imports.all()


class BaseTestPrototypes(utils_testcase.TestCase):

    def setUp(self):
        super(BaseTestPrototypes, self).setUp()

        self.place1, self.place2, self.place3 = game_logic.create_test_map()

        self.account1 = self.accounts_factory.create_account()
        self.account2 = self.accounts_factory.create_account()
        self.account3 = self.accounts_factory.create_account()
        self.account4 = self.accounts_factory.create_account()

        forum_category = forum_models.Category.objects.create(caption='category-1', slug='category-1')
        forum_models.SubCategory.objects.create(caption=conf.settings.FORUM_CATEGORY_UID + '-caption',
                                                uid=conf.settings.FORUM_CATEGORY_UID,
                                                category=forum_category)


def choose_exchange_resources():
    resource_1, resource_2 = places_relations.RESOURCE_EXCHANGE_TYPE.NONE, places_relations.RESOURCE_EXCHANGE_TYPE.NONE
    while resource_1.parameter == resource_2.parameter:
        resource_1 = random.choice(bills.place_resource_exchange.ALLOWED_EXCHANGE_TYPES)
        resource_2 = random.choice(bills.place_resource_exchange.ALLOWED_EXCHANGE_TYPES)
    return resource_1, resource_2


def choose_conversions():
    conversion_1, conversion_2 = None, None
    while conversion_1 == conversion_2:
        conversion_1 = random.choice(bills.place_resource_conversion.CONVERSION.records)
        conversion_2 = random.choice(bills.place_resource_conversion.CONVERSION.records)
    return conversion_1, conversion_2
