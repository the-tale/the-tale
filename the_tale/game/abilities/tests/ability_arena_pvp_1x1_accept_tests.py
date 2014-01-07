# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.workers.environment import workers_environment

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map
from the_tale.game.models import SupervisorTask
from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.abilities.deck.arena_pvp_1x1_accept import ArenaPvP1x1Accept, ABILITY_TASK_STEP
from the_tale.game.abilities.relations import ABILITY_RESULT

from the_tale.game.pvp.models import BATTLE_1X1_STATE, Battle1x1

class ArenaPvP1x1AcceptBaseTests(testcase.TestCase):

    def setUp(self):
        super(ArenaPvP1x1AcceptBaseTests, self).setUp()

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

        self.pvp_balancer = workers_environment.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

        self.battle = self.pvp_balancer.add_to_arena_queue(self.hero_1.id)



class ArenaPvP1x1LeaveQueueAbilityTest(ArenaPvP1x1AcceptBaseTests):

    def setUp(self):
        super(ArenaPvP1x1LeaveQueueAbilityTest, self).setUp()

        self.ability = ArenaPvP1x1Accept()

    def use_attributes(self, step=None, storage=None, pvp_balancer=None):
        return {'data': {'hero_id': self.hero_2.id,
                         'battle': self.battle.id},
                'step': step,
                'main_task_id': 0,
                'storage': storage,
                'pvp_balancer': pvp_balancer}

    def process_ability(self, success=True):
        result, step, postsave_actions = self.ability.use(**self.use_attributes(storage=self.storage))

        self.assertEqual((result, step), (ABILITY_RESULT.CONTINUE, ABILITY_TASK_STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(step=step, pvp_balancer=self.pvp_balancer))

        if success:
            self.assertEqual((result, step, postsave_actions), (ABILITY_RESULT.SUCCESSED, ABILITY_TASK_STEP.SUCCESS, ()))
        else:
            self.assertEqual((result, step, postsave_actions), (ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()))

    def test_process_battle_not_found(self):
        Battle1x1.objects.all().delete()

        self.process_ability(success=False)

    def test_process_wrong_accepted_battle_state(self):
        self.battle.state = BATTLE_1X1_STATE.PROCESSING
        self.battle.save()

        self.process_ability(success=False)

    def test_process_wrong_initiator_battle_state(self):
        battle = self.pvp_balancer.add_to_arena_queue(self.hero_2.id)
        battle.state = BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.process_ability(success=False)

    def test_process_battle_not_in_queue(self):
        self.pvp_balancer.arena_queue.clear()
        self.process_ability(success=False)

    def test_process_success(self):
        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.process_ability()

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)


    def test_process_success_when_initiator_already_has_battle_object(self):
        self.pvp_balancer.add_to_arena_queue(self.hero_2.id)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.process_ability()

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)



class AcceptBattleMethodTests(ArenaPvP1x1AcceptBaseTests):

    def setUp(self):
        super(AcceptBattleMethodTests, self).setUp()

    def accept_battle(self):
        return ArenaPvP1x1Accept.accept_battle(self.pvp_balancer, self.battle.id, self.hero_2.id)

    def test_process_battle_not_found(self):
        Battle1x1.objects.all().delete()

        self.assertTrue(self.accept_battle().is_BATTLE_NOT_FOUND)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_process_wrong_accepted_battle_state(self):
        self.battle.state = BATTLE_1X1_STATE.PROCESSING
        self.battle.save()

        self.assertTrue(self.accept_battle().is_WRONG_ACCEPTED_BATTLE_STATE)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_process_wrong_initiator_battle_state(self):
        battle = self.pvp_balancer.add_to_arena_queue(self.hero_2.id)
        battle.state = BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.assertTrue(self.accept_battle().is_WRONG_INITIATOR_BATTLE_STATE)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_process_battle_not_in_queue(self):
        self.pvp_balancer.arena_queue.clear()

        self.assertTrue(self.accept_battle().is_NOT_IN_QUEUE)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_process_success(self):
        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.assertTrue(self.accept_battle().is_PROCESSED)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)


    def test_process_success_when_initiator_already_has_battle_object(self):
        self.pvp_balancer.add_to_arena_queue(self.hero_2.id)

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.assertTrue(self.accept_battle().is_PROCESSED)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)
