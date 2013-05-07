# coding: utf-8

from common.utils import testcase

from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.models import SupervisorTask

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.workers.environment import workers_environment

from game.pvp.models import Battle1x1
from game.pvp.relations import BATTLE_1X1_STATE
from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.postponed_tasks import AcceptBattleTask, ACCEPT_BATTLE_TASK_STATE

class AcceptBattleTaskTests(testcase.TestCase):

    def setUp(self):
        super(AcceptBattleTaskTests, self).setUp()

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

        workers_environment.deinitialize()
        workers_environment.initialize()
        self.balancer = workers_environment.pvp_balancer
        self.balancer.process_initialize('pvp_balancer')

        self.battle = self.balancer.add_to_arena_queue(self.hero_1.id)

        self.task = AcceptBattleTask(battle_id=self.battle.id, accept_initiator_id=self.account_2.id)

    def test_create(self):
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.battle_id, self.battle.id)
        self.assertEqual(self.task.accept_initiator_id, self.account_2.id)

    def test_serialize(self):
        self.assertEqual(self.task.serialize(), AcceptBattleTask.deserialize(self.task.serialize()).serialize())

    def test_process_battle_not_found(self):
        Battle1x1.objects.all().delete()
        self.task.process(FakePostpondTaskPrototype(), self.balancer)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.BATTLE_NOT_FOUND)

    def test_process_wrong_accepted_battle_state(self):
        self.battle.state = BATTLE_1X1_STATE.PROCESSING
        self.battle.save()
        self.task.process(FakePostpondTaskPrototype(), self.balancer)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.WRONG_ACCEPTED_BATTLE_STATE)

    def test_process_wrong_initiator_battle_state(self):
        battle = self.balancer.add_to_arena_queue(self.hero_2.id)
        battle.state = BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.task.process(FakePostpondTaskPrototype(), self.balancer)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.WRONG_INITIATOR_BATTLE_STATE)

    def test_process_battle_not_in_queue(self):
        self.balancer.arena_queue.clear()
        self.task.process(FakePostpondTaskPrototype(), self.balancer)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.NOT_IN_QUEUE)

    def test_process_success(self):
        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.balancer), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.PROCESSED)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)


    def test_process_success_when_initiator_already_has_battle_object(self):
        self.balancer.add_to_arena_queue(self.hero_2.id)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.balancer), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ACCEPT_BATTLE_TASK_STATE.PROCESSED)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)
