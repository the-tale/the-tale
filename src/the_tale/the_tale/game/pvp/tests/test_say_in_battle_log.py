
import smart_imports

smart_imports.all()


class SayInBattleLogTests(helpers.PvPTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        self.battle_info = self.create_pvp_battle()

        self.task = postponed_tasks.SayInBattleLogTask(speaker_id=self.battle_info.account_1.id, text='some pvp message')

    def test_create(self):
        self.assertEqual(self.task.state, postponed_tasks.SAY_IN_HERO_LOG_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.speaker_id, self.battle_info.account_1.id)

    def test_serialize(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.SayInBattleLogTask.deserialize(self.task.serialize()).serialize())

    def test_process_success(self):
        self.assertFalse(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage),
                         POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertTrue(self.battle_info.hero_1.journal.messages)
        self.assertTrue(self.battle_info.hero_2.journal.messages)

    def test_process_success_without_second_hero(self):
        self.assertFalse(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)

        self.battle_info.storage.release_account_data(self.battle_info.account_2.id)
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage),
                         POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.task.state, postponed_tasks.SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertTrue(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)

    def test_process_success_without_first_hero(self):
        self.assertFalse(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)

        self.battle_info.storage.release_account_data(self.battle_info.account_1.id)

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage),
                         POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.task.state, postponed_tasks.SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertFalse(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)
