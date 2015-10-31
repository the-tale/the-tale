# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.balance import constants as c

from the_tale.game.heroes.habilities import nonbattle
from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE
from the_tale.game.heroes.relations import MODIFIERS

from .. import logic


class HabilitiesNonBattleTest(testcase.TestCase):

    def setUp(self):
        super(HabilitiesNonBattleTest, self).setUp()
        create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = logic.load_hero(account_id=account.id)

    def tearDown(self):
        pass

    def test_charisma(self):
        self.assertTrue(1.0 < nonbattle.CHARISMA().modify_attribute(MODIFIERS.QUEST_MONEY_REWARD, 1.0))

    def test_huckster(self):
        self.assertTrue(1.0 > nonbattle.HUCKSTER().modify_attribute(MODIFIERS.BUY_PRICE, 1.0))
        self.assertTrue(1.0 < nonbattle.HUCKSTER().modify_attribute(MODIFIERS.SELL_PRICE, 1.0))

    def test_dandy(self):
        priorities = {record:record.priority for record in ITEMS_OF_EXPENDITURE.records}
        priorities = nonbattle.DANDY().modify_attribute(MODIFIERS.ITEMS_OF_EXPENDITURE_PRIORITIES, priorities)

        self.assertEqual(ITEMS_OF_EXPENDITURE.INSTANT_HEAL.priority, priorities[ITEMS_OF_EXPENDITURE.INSTANT_HEAL])
        self.assertEqual(ITEMS_OF_EXPENDITURE.USELESS.priority, priorities[ITEMS_OF_EXPENDITURE.USELESS])
        self.assertEqual(ITEMS_OF_EXPENDITURE.IMPACT.priority, priorities[ITEMS_OF_EXPENDITURE.IMPACT])

        self.assertTrue(ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT.priority < priorities[ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT])
        self.assertTrue(ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT.priority < priorities[ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT])
        self.assertTrue(ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT.priority < priorities[ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT])

    @mock.patch('the_tale.game.balance.constants.ARTIFACT_FOR_QUEST_PROBABILITY', 0)
    def test_businessman(self):
        self.assertFalse(any(self.hero.can_get_artifact_for_quest() for i in xrange(1000)))
        self.hero.abilities.add(nonbattle.BUSINESSMAN.get_id())
        self.assertTrue(any(self.hero.can_get_artifact_for_quest() for i in xrange(1000)))

    def test_picky(self):
        with self.check_increased(lambda: self.hero.rare_artifact_probability_multiplier):
            with self.check_increased(lambda: self.hero.epic_artifact_probability_multiplier):
                self.hero.abilities.add(nonbattle.PICKY.get_id())

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

        self.assertEqual(self.hero.max_bag_size, c.MAX_BAG_SIZE + 2)


    def test_diplomatic(self):
        old_power_modifier = self.hero.politics_power_multiplier()

        self.hero.abilities.add(nonbattle.DIPLOMATIC.get_id())

        self.assertTrue(old_power_modifier < self.hero.politics_power_multiplier())


    def test_open_minded(self):
        with self.check_increased(lambda: self.hero.habits_increase_modifier):
            self.hero.abilities.add(nonbattle.OPEN_MINDED.get_id())


    def test_selfish(self):
        from the_tale.game.quests import relations as quests_relations

        with self.check_increased(lambda: self.hero.modify_quest_priority(quests_relations.QUESTS.HUNT)):
            with self.check_not_changed(lambda: self.hero.modify_quest_priority(quests_relations.QUESTS.SPYING)):
                self.hero.abilities.add(nonbattle.SELFISH.get_id())
