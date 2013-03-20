# coding: utf-8
import mock

from common.utils import testcase
from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.prototypes import TimePrototype

from game.actions.prototypes import ActionIdlenessPrototype

from game.quests.postponed_tasks import ChooseQuestLineTask, CHOOSE_QUEST_LINE_STATE
from game.quests.quests_generator.tests.helpers import QuestWith2ChoicePoints, patch_quests_list

from game.quests.tests.helpers import QuestTestsMixin


class ChooseQuestLineTaskTest(testcase.TestCase, QuestTestsMixin):

    def setUp(self):
        super(ChooseQuestLineTaskTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_id = account_id
        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero =self.storage.accounts_to_heroes[account_id]

    def create_task(self, choice_point, choice, quest_id=None, account_id=None):

        if account_id is None:
            account_id = self.account_id

        if quest_id is None:
            quest_id = self.turn_to_quest(self.storage, self.hero.id).id

        task = ChooseQuestLineTask(account_id=account_id,
                                   quest_id=quest_id,
                                   choice_point=choice_point,
                                   choice=choice)
        return task

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_create(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.UNPROCESSED)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_serialization(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.serialize(), ChooseQuestLineTask.deserialize(task.serialize()).serialize())

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_unknown_choice(self):
        task = self.create_task(choice_point='choose_1', choice='unknown_choice')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.UNKNOWN_CHOICE)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_wrong_account(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        task = self.create_task(choice_point='choose_1', choice='unknown_choice', account_id=account_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.QUEST_NOT_FOUND)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_wrong_point(self):
        task = self.create_task(choice_point='unknown_point', choice='choice_1_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.WRONG_POINT)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    # TODO: patch not QuestPrototype, but Line
    @mock.patch('game.quests.prototypes.QuestPrototype.is_choice_available', lambda self, choice: False)
    def test_line_not_available(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.LINE_NOT_AVAILABLE)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_already_chosen(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.PROCESSED)

        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.ALREADY_CHOSEN)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_quest_not_found(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1', quest_id=666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.QUEST_NOT_FOUND)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_success(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.PROCESSED)


    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_second_choice_before_first_completed(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_2')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.PROCESSED)

        task = self.create_task(choice_point='choose_2', choice='choice_2_1')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.UNKNOWN_CHOICE)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_second_choice_after_first_completed(self):
        task = self.create_task(choice_point='choose_1', choice='choice_1_2')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_QUEST_LINE_STATE.PROCESSED)

        current_time = TimePrototype.get_current_time()

        while True:
            self.assertNotEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionIdlenessPrototype.TYPE)

            task = self.create_task(choice_point='choose_2', choice='choice_2_1')

            if task.process(FakePostpondTaskPrototype(), self.storage) == POSTPONED_TASK_LOGIC_RESULT.ERROR:
                break

            self.storage.process_turn()
            self.storage.save_changed_data()
            current_time.increment_turn()
