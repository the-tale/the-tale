# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.balance import constants as c

from the_tale.game.heroes.habilities import nonbattle
from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE


class HabilitiesNonBattleTest(testcase.TestCase):

    def setUp(self):
        super(HabilitiesNonBattleTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

    def tearDown(self):
        pass

    def test_charisma(self):
        self.assertTrue(100 < nonbattle.CHARISMA().update_quest_reward(self.hero, 100))

    def test_hackster(self):
        self.assertTrue(100 > nonbattle.HUCKSTER().update_buy_price(self.hero, 100))
        self.assertTrue(100 < nonbattle.HUCKSTER().update_sell_price(self.hero, 100))

    def test_dandy(self):
        priorities = {record:record.priority for record in ITEMS_OF_EXPENDITURE.records}
        priorities = nonbattle.DANDY().update_items_of_expenditure_priorities(self.hero, priorities)

        self.assertEqual(ITEMS_OF_EXPENDITURE.INSTANT_HEAL.priority, priorities[ITEMS_OF_EXPENDITURE.INSTANT_HEAL])
        self.assertEqual(ITEMS_OF_EXPENDITURE.USELESS.priority, priorities[ITEMS_OF_EXPENDITURE.USELESS])
        self.assertEqual(ITEMS_OF_EXPENDITURE.IMPACT.priority, priorities[ITEMS_OF_EXPENDITURE.IMPACT])

        self.assertTrue(ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT.priority < priorities[ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT])
        self.assertTrue(ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT.priority < priorities[ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT])

    def test_businessman(self):
        self.assertFalse(any(self.hero.can_get_artifact_for_quest() for i in xrange(200)))
        self.hero.abilities.add(nonbattle.BUSINESSMAN.get_id())
        self.assertTrue(any(self.hero.can_get_artifact_for_quest() for i in xrange(200)))

    def test_picky(self):
        self.assertFalse(any(self.hero.can_buy_better_artifact() for i in xrange(200)))
        self.hero.abilities.add(nonbattle.PICKY.get_id())
        self.assertTrue(any(self.hero.can_buy_better_artifact() for i in xrange(200)))

    def test_ethereal_magnet(self):
        old_crit_chance = self.hero.might_crit_chance
        self.hero.abilities.add(nonbattle.ETHEREAL_MAGNET.get_id())
        self.assertTrue(self.hero.might_crit_chance > old_crit_chance)

    def test_wanderer(self):
        old_speed = self.hero.move_speed
        self.hero.abilities.add(nonbattle.WANDERER.get_id())
        self.assertTrue(self.hero.move_speed > old_speed)

    def test_gifted(self):
        old_experience_modifier = self.hero.experience_modifier

        self.hero.abilities.add(nonbattle.GIFTED.get_id())

        self.assertTrue(old_experience_modifier < self.hero.experience_modifier)

    def test_thrifty(self):
        self.assertEqual(self.hero.max_bag_size, c.MAX_BAG_SIZE)

        self.hero.abilities.add(nonbattle.THRIFTY.get_id())

        self.assertEqual(self.hero.max_bag_size, c.MAX_BAG_SIZE + 1)


    def test_diplomatic(self):
        old_power_modifier = self.hero.person_power_modifier

        self.hero.abilities.add(nonbattle.DIPLOMATIC.get_id())

        self.assertTrue(old_power_modifier < self.hero.person_power_modifier)
