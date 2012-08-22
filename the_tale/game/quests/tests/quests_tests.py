# coding: utf-8

from common.utils.testcase import TestCase

from game.logic import create_test_bundle, create_test_map
from game.prototypes import TimePrototype
from game.quests.quests_generator.lines import QUESTS
from game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype
from game.quests.quests_generator.tests.helpers import patch_quests_list
from game.quests.quests_generator.lines.delivery import Delivery
from game.quests.quests_generator.lines.not_my_work import NotMyWork
from game.quests.quests_generator.lines.help import Help

class QuestsTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('QuestActionTest')
        self.hero = self.bundle.tests_get_hero()
        self.action_idl = self.bundle.tests_get_last_action()

        self.hero.preferences.set_mob_id('rat')
        self.hero.save()

    def tearDown(self):
        pass

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.bundle.process_turn()
            current_time.increment_turn()


for QuestClass in QUESTS:

    quests = [QuestClass]

    if QuestClass in (Help, NotMyWork):
        quests.append(Delivery)

    @patch_quests_list(quests)
    def quest_test_method(self):

        current_time = TimePrototype.get_current_time()

        while self.bundle.tests_get_last_action().TYPE != ActionQuestPrototype.TYPE:
            self.bundle.process_turn()
            current_time.increment_turn()

        self.complete_quest()

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionIdlenessPrototype.TYPE)

    setattr(QuestsTest, 'test_%s' % QuestClass.type(), quest_test_method)
