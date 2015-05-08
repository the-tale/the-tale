# coding: utf-8

import mock

from the_tale.finances.shop.postponed_tasks import BuyRandomPremiumChest
from the_tale.finances.shop.tests import base_buy_task
from the_tale.finances.shop import relations
from the_tale.accounts.prototypes import RandomPremiumRequestPrototype

from the_tale.game.logic_storage import LogicStorage


@mock.patch('the_tale.finances.shop.postponed_tasks.BuyRandomPremiumChest.get_reward_type',
            lambda self: relations.RANDOM_PREMIUM_CHEST_REWARD.NORMAL_ARTIFACT)
class BuyRandomPremiumChestTask__NormalArtifact_Tests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTask__NormalArtifact_Tests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.assertEqual(self.hero.bag.occupation, 0)


    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertTrue(self.hero.bag.values()[0].rarity.is_NORMAL)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)


@mock.patch('the_tale.finances.shop.postponed_tasks.BuyRandomPremiumChest.get_reward_type',
            lambda self: relations.RANDOM_PREMIUM_CHEST_REWARD.RARE_ARTIFACT)
class BuyRandomPremiumChestTask__RareArtifact_Tests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTask__RareArtifact_Tests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.assertEqual(self.hero.bag.occupation, 0)


    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertTrue(self.hero.bag.values()[0].rarity.is_RARE)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)


@mock.patch('the_tale.finances.shop.postponed_tasks.BuyRandomPremiumChest.get_reward_type',
            lambda self: relations.RANDOM_PREMIUM_CHEST_REWARD.EPIC_ARTIFACT)
class BuyRandomPremiumChestTask__EpicArtifact_Tests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTask__EpicArtifact_Tests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.assertEqual(self.hero.bag.occupation, 0)


    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertTrue(self.hero.bag.values()[0].rarity.is_EPIC)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)


@mock.patch('the_tale.finances.shop.postponed_tasks.BuyRandomPremiumChest.get_reward_type',
            lambda self: relations.RANDOM_PREMIUM_CHEST_REWARD.ENERGY)
class BuyRandomPremiumChestTask__Energy_Tests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTask__Energy_Tests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.energy_bonus = 0


    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.energy_bonus, 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertEqual(self.hero.energy_bonus, relations.RANDOM_PREMIUM_CHEST_REWARD.ENERGY.arguments['energy'])
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)


@mock.patch('the_tale.finances.shop.postponed_tasks.BuyRandomPremiumChest.get_reward_type',
            lambda self: relations.RANDOM_PREMIUM_CHEST_REWARD.EXPERIENCE)
class BuyRandomPremiumChestTask__Experience_Tests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTask__Experience_Tests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.assertEqual(self.hero.experience, 0)
        self.assertEqual(self.hero.level, 1)


    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.level, 1)
        self.assertEqual(self.hero.experience, 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertTrue(self.hero.level > 1 or self.hero.experience > 0)
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)


class BuyRandomPremiumChestTaskTests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyRandomPremiumChestTaskTests, self).setUp()

        self.task = BuyRandomPremiumChest(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 0)

    def _check_used(self):
        self.assertEqual(RandomPremiumRequestPrototype._db_count(), 1)
