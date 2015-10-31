# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.prototypes import TimePrototype

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.quests.tests import helpers as quests_helpers

from the_tale.game.actions import prototypes


class QuestActionTests(testcase.TestCase):

    def setUp(self):
        super(QuestActionTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_quest = prototypes.ActionQuestPrototype.create(hero=self.hero)


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_quest.leader, True)
        self.assertEqual(self.action_quest.state, self.action_quest.STATE.SEARCHING)
        self.assertEqual(self.action_quest.bundle_id, self.action_idl.bundle_id)
        self.assertFalse(self.hero.quests.has_quests)
        self.storage._test_save()

    def test_setup_quest(self):
        quests_helpers.setup_quest(self.hero)

        self.assertEqual(self.action_quest.state, self.action_quest.STATE.PROCESSING)
        self.assertTrue(self.hero.quests.has_quests)
        self.storage._test_save()

    def test_one_step(self):
        self.storage.process_turn()
        # quest can create new action on first step
        self.assertTrue(2 <= len(self.hero.actions.actions_list) <= 3)
        self.storage._test_save()


    def test_step_with_no_quest(self):
        quests_helpers.setup_quest(self.hero)

        self.hero.quests.pop_quest()
        self.storage.process_turn()
        self.assertEqual(self.action_idl.leader, True)


    def test_need_equipping(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.need_equipping', lambda hero: True):
            self.storage.process_turn()

        self.assertEqual(self.action_quest.state, self.action_quest.STATE.EQUIPPING)
        self.assertTrue(self.hero.actions.current_action.TYPE.is_EQUIPPING)

        self.storage.process_turn()

        self.assertEqual(self.action_quest.state, self.action_quest.STATE.EQUIPPING)
        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        self.storage.process_turn()

        self.assertEqual(self.action_quest.state, self.action_quest.STATE.PROCESSING)


    def test_full_quest(self):
        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

        self.storage._test_save()

        self.assertFalse(self.hero.quests.has_quests)
