# coding: utf-8
import mock
from common.utils import testcase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage


from game.logic import create_test_map
from game.actions.prototypes import ActionQuestPrototype
from game.quests.logic import create_random_quest_for_hero
from game.quests.models import Quest, QuestsHeroes
from game.prototypes import TimePrototype

class QuestActionTest(testcase.TestCase):

    def setUp(self):
        super(QuestActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(hero=self.hero, quest=self.quest)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_quest.leader, True)
        self.assertEqual(self.action_quest.bundle_id, self.action_idl.bundle_id)
        self.assertTrue(self.hero.quests.has_quests)
        self.storage._test_save()

    def test_one_step(self):
        self.storage.process_turn()
        # quest can create new action on first step
        self.assertTrue(2 <= len(self.hero.actions.actions_list) <= 3)
        self.storage._test_save()


    def test_full_quest(self):

        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

        self.storage._test_save()

        self.assertFalse(self.hero.quests.has_quests)
