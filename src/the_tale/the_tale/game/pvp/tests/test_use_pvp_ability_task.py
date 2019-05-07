
import smart_imports

smart_imports.all()


class UsePvPAbilityTests(helpers.PvPTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        self.battle_info = self.create_pvp_battle()

        self.ability = random.choice(list(abilities.ABILITIES.values()))

        self.task = postponed_tasks.UsePvPAbilityTask(account_id=self.battle_info.account_1.id,
                                                      ability_id=self.ability.TYPE)

    def test_create(self):
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.account_id, self.battle_info.account_1.id)
        self.assertEqual(self.task.ability_id, self.ability.TYPE)

    def test_serialize(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.UsePvPAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_process_hero_not_found(self):
        self.battle_info.storage.release_account_data(self.battle_info.account_1.id)
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.HERO_NOT_FOUND)

    def test_process_enemy_hero_not_found(self):
        self.battle_info.storage.release_account_data(self.battle_info.account_2.id)
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.ENEMY_HERO_NOT_FOUND)

    def test_wrong_ability_id(self):
        task = postponed_tasks.UsePvPAbilityTask(account_id=self.battle_info.account_1.id,
                                                 ability_id='wrong_ability_id')
        task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage)
        self.assertEqual(task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.WRONG_ABILITY_ID)

    def test_no_resources(self):
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.NO_ENERGY)

    def test_process_success(self):
        self.battle_info.meta_action.hero_1_pvp.set_energy(1)

        hero_pvp, enemy_pvp = logic.get_arena_heroes_pvp(self.battle_info.hero_1)
        hero_pvp.set_energy(1)

        self.assertFalse(self.battle_info.hero_1.journal.messages)
        self.assertFalse(self.battle_info.hero_2.journal.messages)

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.battle_info.storage),
                         POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.PROCESSED)

        self.assertTrue(self.battle_info.hero_1.journal.messages)
        self.assertTrue(self.battle_info.hero_2.journal.messages)

        # проверка, что сообщение у противника появится только на следующем ходу
        self.assertTrue(self.battle_info.hero_1.journal.ui_info())
        self.assertFalse(self.battle_info.hero_2.journal.ui_info())

        hero_pvp, enemy_pvp = logic.get_arena_heroes_pvp(self.battle_info.hero_1)

        self.assertEqual(hero_pvp.energy, 0)
