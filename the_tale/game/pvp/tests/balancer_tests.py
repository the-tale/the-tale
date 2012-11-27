# coding: utf-8
import mock
import datetime

from django.test import TestCase
from dext.settings import settings

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.workers.environment import workers_environment

from game.models import SupervisorTask

from game.pvp.models import Battle1x1, BATTLE_1X1_STATE
from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.workers.balancer import QueueRecord, BalancingRecord
from game.pvp.exceptions import PvPException

from game.pvp.conf import pvp_settings

class BalancerTestsBase(TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.hero_1 = HeroPrototype.get_by_account_id(account_1_id)
        self.hero_2 = HeroPrototype.get_by_account_id(account_2_id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        Battle1x1Prototype.create(self.account_1)

        self.worker = workers_environment.pvp_balancer
        self.worker.process_initialize('pvp_balancer')



class BalancerTests(BalancerTestsBase):

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.arena_queue, {})
        self.assertEqual(Battle1x1.objects.all().count(), 0)

    def test_process_add_to_arena_queue(self):
        battle = self.worker.add_to_arena_queue(self.hero_1.id)
        self.assertEqual(len(self.worker.arena_queue), 1)
        self.assertEqual(self.worker.arena_queue.values()[0], QueueRecord(account_id=self.account_1.id,
                                                                          battle_id=battle.id,
                                                                          created_at=battle.created_at,
                                                                          hero_level=self.hero_1.level))


    def test_process_add_to_arena_queue_two_requests_from_one_account(self):
        Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_1.id))
        self.assertRaises(PvPException, Battle1x1Prototype.create, AccountPrototype.get_by_id(self.account_1.id))

    def test_process_add_to_arena_queue_second_record(self):
        self.worker.add_to_arena_queue(self.hero_1.id)
        self.worker.add_to_arena_queue(self.hero_2.id)
        self.assertEqual(len(self.worker.arena_queue), 2)

    def test_process_leave_queue_not_waiting_state(self):
        battle_1 = Battle1x1Prototype.create(self.account_1)

        battle_1.set_enemy(self.account_2)
        battle_1.save()

        self.assertTrue(Battle1x1Prototype.get_by_id(battle_1.id).state.is_prepairing)

        self.worker.leave_arena_queue(self.hero_1.id)

        self.assertTrue(Battle1x1Prototype.get_by_id(battle_1.id).state.is_prepairing)

    def test_process_leave_queue_waiting_state(self):
        battle = self.worker.add_to_arena_queue(self.hero_1.id)

        self.assertEqual(len(self.worker.arena_queue), 1)

        self.worker.leave_arena_queue(self.hero_1.id)

        self.assertEqual(len(self.worker.arena_queue), 0)

        self.assertTrue(Battle1x1Prototype.get_by_id(battle.id).state.is_leave_queue)



class BalancerBalancingTests(BalancerTestsBase):

    def setUp(self):

        super(BalancerBalancingTests, self).setUp()

        self.battle_1 = self.worker.add_to_arena_queue(self.hero_1.id)
        self.battle_2 = self.worker.add_to_arena_queue(self.hero_2.id)

        self.test_record_1 = QueueRecord(account_id=0, created_at=0, battle_id=0, hero_level=1)
        self.test_record_2 = QueueRecord(account_id=1, created_at=1, battle_id=0, hero_level=4)

    def battle_1_record(self, created_at_delta=datetime.timedelta(seconds=0)):
        return QueueRecord(account_id=self.account_1.id,
                           battle_id=self.battle_1.id,
                           created_at=self.battle_1.created_at + created_at_delta,
                           hero_level=self.hero_1.level)

    def battle_2_record(self, created_at_delta=datetime.timedelta(seconds=0)):
        return QueueRecord(account_id=self.account_2.id,
                           battle_id=self.battle_2.id,
                           created_at=self.battle_2.created_at + created_at_delta,
                           hero_level=self.hero_2.level)


    def test_get_prepaired_queue_empty(self):
        self.worker.leave_arena_queue(self.hero_1.id)
        self.worker.leave_arena_queue(self.hero_2.id)

        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(records, [])
        self.assertEqual(records_to_remove, [])

    def test_get_prepaired_queue_one_record(self):
        self.worker.leave_arena_queue(self.hero_2.id)

        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(len(records), 1)
        self.assertEqual(records_to_remove, [])

        record = records[0]
        self.assertEqual(record[2], self.battle_1_record())
        self.assertTrue(record[0] <= record[1])

    def test_get_prepaired_queue_one_record_test_time_delta(self):
        battle_1_record = self.battle_1_record(created_at_delta=-datetime.timedelta(seconds=float(pvp_settings.BALANCING_TIMEOUT) / pvp_settings.BALANCING_MAX_LEVEL_DELTA * 2))
        self.worker.arena_queue[self.account_1.id] = battle_1_record

        self.worker.leave_arena_queue(self.hero_2.id)

        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(len(records), 1)
        self.assertEqual(records_to_remove, [])

        record = records[0]
        self.assertEqual(record[2], battle_1_record)
        self.assertEqual(record[0], -6)
        self.assertEqual(record[1], 8)

    def test_get_prepaired_queue_one_record_timeout(self):
        battle_1_record = self.battle_1_record(created_at_delta=-datetime.timedelta(seconds=2))
        self.worker.arena_queue[self.account_1.id] = battle_1_record

        self.worker.leave_arena_queue(self.hero_2.id)

        with mock.patch('game.pvp.conf.pvp_settings.BALANCING_TIMEOUT', 0):
            records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(records, [])
        self.assertEqual(len(records_to_remove), 1)

        self.assertEqual(records_to_remove, [battle_1_record])

    def test_get_prepaired_queue_two_records(self):
        records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(len(records), 2)
        self.assertEqual(records_to_remove, [])

        record_1 = records[0]
        record_2 = records[1]
        self.assertEqual(record_1[2], self.battle_1_record())
        self.assertTrue(record_1[0] <= record_1[1])
        self.assertEqual(record_2[2], self.battle_2_record())
        self.assertTrue(record_2[0] <= record_2[1])


    def test_get_prepaired_queue_two_records_one_timeout(self):
        battle_1_record = self.battle_1_record(created_at_delta=-datetime.timedelta(seconds=2))
        battle_2_record = self.battle_2_record(created_at_delta=-datetime.timedelta(seconds=1))

        self.worker.arena_queue[self.account_1.id] = battle_1_record
        self.worker.arena_queue[self.account_2.id] = battle_2_record

        with mock.patch('game.pvp.conf.pvp_settings.BALANCING_TIMEOUT', 1):
            records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(len(records), 1)
        self.assertEqual(len(records_to_remove), 1)

        record_2 = records[0]
        self.assertEqual(records_to_remove, [battle_1_record])
        self.assertEqual(record_2[2], battle_2_record)
        self.assertTrue(record_2[0] <= record_2[1])


    def test_search_battles_empty(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_search_battles_one_record(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([(1, 2, 'record_1')])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_has_intersections_false(self):
        record_1 = BalancingRecord(min_level=0, max_level=3, record=self.test_record_1)
        record_2 = BalancingRecord(min_level=3, max_level=5, record=self.test_record_2)
        self.assertFalse(record_1.has_intersections(record_2))

    def test_has_intersections_true(self):
        record_1 = BalancingRecord(min_level=0, max_level=4, record=self.test_record_1)
        record_2 = BalancingRecord(min_level=1, max_level=5, record=self.test_record_2)
        self.assertTrue(record_1.has_intersections(record_2))

    def test_search_battles_two_records_unsuitable(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([BalancingRecord(min_level=0, max_level=3, record=self.test_record_1),
                                                                        BalancingRecord(min_level=3, max_level=5, record=self.test_record_2)])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_search_battles_two_records_suitable(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([BalancingRecord(min_level=0, max_level=4, record=self.test_record_1),
                                                                        BalancingRecord(min_level=1, max_level=5, record=self.test_record_2)])
        self.assertEqual(battle_pairs, [(self.test_record_1, self.test_record_2)])
        self.assertEqual(records_to_exclude, [self.test_record_1, self.test_record_2])


    def test_clean_queue(self):
        self.worker._clean_queue([], [])
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING).count(), 2)
        self.worker._clean_queue([self.battle_1_record()], [self.battle_2_record()])
        self.assertEqual(self.worker.arena_queue, {})
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.ENEMY_NOT_FOND).count(), 1)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING).count(), 1)


    def test_initiate_battle(self):

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.worker._initiate_battle(self.battle_1_record(), self.battle_2_record())

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle_1.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle_2.id).enemy_id, self.account_1.id)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)
