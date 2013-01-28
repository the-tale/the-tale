# coding: utf-8
import random

from django.test import TestCase

from dext.settings import settings

from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.postponed_tasks import ChangePvPStyleTask, CHANGE_PVP_STYLE_TASK_STATE
from game.pvp.combat_styles import COMBAT_STYLES

class ChangePvPStyleTests(TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.battle = Battle1x1Prototype.create(self.account_1)
        self.battle.set_enemy(self.account_2)
        self.battle.save()

        self.combat_style = random.choice(COMBAT_STYLES.values())

        self.task = ChangePvPStyleTask(battle_id=self.battle.id, account_id=self.account_1.id, combat_style_id=self.combat_style.type)

    def test_create(self):
        self.assertEqual(self.task.state, CHANGE_PVP_STYLE_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.battle_id, self.battle.id)
        self.assertEqual(self.task.account_id, self.account_1.id)
        self.assertEqual(self.task.combat_style_id, self.combat_style.type)

    def test_serialize(self):
        self.assertEqual(self.task, ChangePvPStyleTask.deserialize(self.task.serialize()))

    def test_process_hero_not_found(self):
        self.storage.release_account_data(self.account_1)
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, CHANGE_PVP_STYLE_TASK_STATE.HERO_NOT_FOUND)

    def test_wrong_style_id(self):
        task = ChangePvPStyleTask(battle_id=self.battle.id, account_id=self.account_1.id, combat_style_id=666)
        task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(task.state, CHANGE_PVP_STYLE_TASK_STATE.WRONG_STYLE_ID)

    def test_no_resources(self):
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, CHANGE_PVP_STYLE_TASK_STATE.NO_RESOURCES)

    def test_process_success(self):
        self.assertEqual(self.hero_1.pvp_combat_style, None)

        self.hero_1.pvp_rage = self.combat_style.cost_rage
        self.hero_1.pvp_initiative = self.combat_style.cost_initiative + 1
        self.hero_1.pvp_concentration = self.combat_style.cost_concentration + 2

        old_hero_1_last_message = self.hero_1.messages[-1]
        old_hero_2_last_message = self.hero_2.messages[-1]

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, CHANGE_PVP_STYLE_TASK_STATE.PROCESSED)

        self.assertNotEqual(old_hero_1_last_message, self.hero_1.messages[-1])
        self.assertNotEqual(old_hero_2_last_message, self.hero_2.messages[-1])

        self.assertEqual(self.hero_1.pvp_rage, 0)
        self.assertEqual(self.hero_1.pvp_initiative, 1)
        self.assertEqual(self.hero_1.pvp_concentration, 2)

        self.assertEqual(self.hero_1.pvp_combat_style, self.combat_style.type)
