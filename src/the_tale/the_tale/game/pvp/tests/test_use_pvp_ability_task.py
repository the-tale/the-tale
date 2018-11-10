
import smart_imports

smart_imports.all()


class UsePvPAbilityTests(utils_testcase.TestCase):

    def setUp(self):
        super(UsePvPAbilityTests, self).setUp()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.battle = prototypes.Battle1x1Prototype.create(self.account_1)
        self.battle.set_enemy(self.account_2)
        self.battle.save()

        self.ability = random.choice(list(abilities.ABILITIES.values()))

        self.task = postponed_tasks.UsePvPAbilityTask(battle_id=self.battle.id, account_id=self.account_1.id, ability_id=self.ability.TYPE)

        self.meta_action_battle = actions_meta_actions.ArenaPvP1x1.create(self.storage, self.hero_1, self.hero_2)
        self.meta_action_battle.set_storage(self.storage)

        actions_prototypes.ActionMetaProxyPrototype.create(hero=self.hero_1, _bundle_id=self.hero_1.actions.current_action.bundle_id, meta_action=self.meta_action_battle)
        actions_prototypes.ActionMetaProxyPrototype.create(hero=self.hero_2, _bundle_id=self.hero_1.actions.current_action.bundle_id, meta_action=self.meta_action_battle)

    def test_create(self):
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.battle_id, self.battle.id)
        self.assertEqual(self.task.account_id, self.account_1.id)
        self.assertEqual(self.task.ability_id, self.ability.TYPE)

    def test_serialize(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.UsePvPAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_process_battle_not_found(self):
        prototypes.Battle1x1Prototype._db_all().delete()
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.BATTLE_FINISHED)

    def test_process_hero_not_found(self):
        self.storage.release_account_data(self.account_1.id)
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.HERO_NOT_FOUND)

    def test_wrong_ability_id(self):
        task = postponed_tasks.UsePvPAbilityTask(battle_id=self.battle.id, account_id=self.account_1.id, ability_id='wrong_ability_id')
        task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.WRONG_ABILITY_ID)

    def test_no_resources(self):
        self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.NO_ENERGY)

    def test_process_success(self):
        self.meta_action_battle.hero_1_pvp.set_energy(1)

        old_hero_1_last_message = self.hero_1.journal.messages[-1]
        old_hero_2_last_message = self.hero_2.journal.messages[-1]

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.USE_PVP_ABILITY_TASK_STATE.PROCESSED)

        self.assertNotEqual(old_hero_1_last_message, self.hero_1.journal.messages[-1])
        self.assertNotEqual(old_hero_2_last_message, self.hero_2.journal.messages[-1])

        self.assertNotEqual(old_hero_1_last_message.ui_info(), self.hero_1.journal.ui_info()[-1])
        self.assertEqual(old_hero_2_last_message.ui_info(), self.hero_2.journal.ui_info()[-1])

        self.assertEqual(self.meta_action_battle.hero_1_pvp.energy, 0)
