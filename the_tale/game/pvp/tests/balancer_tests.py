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

from game.pvp.models import Battle1x1
from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.workers.balancer import QueueRecord

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

        Battle1x1Prototype.create(AccountPrototype.get_by_id(account_1_id))

        self.worker = workers_environment.pvp_balancer
        self.worker.process_initialize('pvp_balancer')



class BalancerTests(BalancerTestsBase):

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.arena_queue, {})
        self.assertEqual(Battle1x1.objects.all().count(), 0)

    def test_process_add_to_arena_queue(self):
        battle = Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_1.id))
        self.worker.process_add_to_arena_queue(battle.id)
        self.assertEqual(len(self.worker.arena_queue), 1)
        self.assertEqual(self.worker.arena_queue.values()[0], QueueRecord(account_id=self.account_1.id,
                                                                          battle_id=battle.id,
                                                                          created_at=battle.created_at,
                                                                          hero_level=self.hero_1.level))


    def test_process_add_to_arena_queue_two_requests_from_one_account(self):
        from django.db import IntegrityError
        Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_1.id))
        self.assertRaises(IntegrityError, Battle1x1Prototype.create, AccountPrototype.get_by_id(self.account_1.id))

    def test_process_add_to_arena_queue_second_record(self):
        battle_1 = Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_1.id))
        battle_2 = Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_2.id))
        self.worker.process_add_to_arena_queue(battle_1.id)
        self.worker.process_add_to_arena_queue(battle_2.id)
        self.assertEqual(len(self.worker.arena_queue), 2)


class BalancerBalancingTests(BalancerTestsBase):

    def setUp(self):

        super(BalancerBalancingTests, self).setUp()

        self.battle_1 = Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_1.id))
        self.battle_2 = Battle1x1Prototype.create(AccountPrototype.get_by_id(self.account_2.id))

    @property
    def battle_1_record(self):
        return QueueRecord(account_id=self.account_1.id,
                           battle_id=self.battle_1.id,
                           created_at=self.battle_1.created_at,
                           hero_level=self.hero_1.level)

    @property
    def battle_2_record(self):
        return QueueRecord(account_id=self.account_2.id,
                           battle_id=self.battle_2.id,
                           created_at=self.battle_2.created_at,
                           hero_level=self.hero_2.level)



    def test_get_prepaired_queue_empty(self):
        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(records, [])
        self.assertEqual(records_to_remove, [])

    def test_get_prepaired_queue_one_record(self):
        self.worker.process_add_to_arena_queue(self.battle_1.id)
        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(len(records), 1)
        self.assertEqual(records_to_remove, [])

        record = records[0]
        self.assertEqual(record[2], self.battle_1_record)
        self.assertTrue(record[0] <= record[1])

    def test_get_prepaired_queue_one_record_test_time_delta(self):
        self.battle_1.model.created_at -= datetime.timedelta(seconds=float(pvp_settings.BALANCING_TIMEOUT) / pvp_settings.BALANCING_MAX_LEVEL_DELTA * 2)
        self.battle_1.save()

        self.worker.process_add_to_arena_queue(self.battle_1.id)

        records, records_to_remove = self.worker._get_prepaired_queue()
        self.assertEqual(len(records), 1)
        self.assertEqual(records_to_remove, [])

        record = records[0]
        self.assertEqual(record[2], self.battle_1_record)
        self.assertEqual(record[0], -1)
        self.assertEqual(record[1], 3)

    def test_get_prepaired_queue_one_record_timeout(self):

        self.battle_1.model.created_at -= datetime.timedelta(seconds=1)
        self.battle_1.save()

        self.worker.process_add_to_arena_queue(self.battle_1.id)

        with mock.patch('game.pvp.conf.pvp_settings.BALANCING_TIMEOUT', 0):
            records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(records, [])
        self.assertEqual(len(records_to_remove), 1)

        self.assertEqual(records_to_remove, [self.battle_1_record])

    def test_get_prepaired_queue_two_records(self):
        self.worker.process_add_to_arena_queue(self.battle_1.id)
        self.worker.process_add_to_arena_queue(self.battle_2.id)

        records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(len(records), 2)
        self.assertEqual(records_to_remove, [])

        record_1 = records[0]
        record_2 = records[1]
        self.assertEqual(record_1[2], self.battle_1_record)
        self.assertTrue(record_1[0] <= record_1[1])
        self.assertEqual(record_2[2], self.battle_2_record)
        self.assertTrue(record_2[0] <= record_2[1])


    def test_get_prepaired_queue_two_records_one_timeout(self):
        self.battle_1.model.created_at -= datetime.timedelta(seconds=2)
        self.battle_1.save()

        self.battle_2.model.created_at -= datetime.timedelta(seconds=1)
        self.battle_2.save()

        self.worker.process_add_to_arena_queue(self.battle_1.id)
        self.worker.process_add_to_arena_queue(self.battle_2.id)

        with mock.patch('game.pvp.conf.pvp_settings.BALANCING_TIMEOUT', 1):
            records, records_to_remove = self.worker._get_prepaired_queue()

        self.assertEqual(len(records), 1)
        self.assertEqual(len(records_to_remove), 1)

        record_2 = records[0]
        self.assertEqual(records_to_remove, [self.battle_1_record])
        self.assertEqual(record_2[2], self.battle_2_record)
        self.assertTrue(record_2[0] <= record_2[1])


    def test_search_battles_empty(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_search_battles_one_record(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([(1, 2, 'record_1')])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_search_battles_two_records_unsuitable(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([(1, 2, 'record_1'),
                                                                        (3, 4, 'record_2')])
        self.assertEqual(battle_pairs, [])
        self.assertEqual(records_to_exclude, [])

    def test_search_battles_two_records_suitable(self):
        battle_pairs, records_to_exclude = self.worker._search_battles([(1, 3, 'record_1'),
                                                                        (3, 4, 'record_2')])
        self.assertEqual(battle_pairs, [('record_1', 'record_2')])
        self.assertEqual(records_to_exclude, ['record_1', 'record_2'])


    def test_clean_queue(self):
        self.worker.process_add_to_arena_queue(self.battle_1.id)
        self.worker.process_add_to_arena_queue(self.battle_2.id)

        self.worker._clean_queue([], [])
        self.assertEqual(Battle1x1.objects.all().count(), 2)
        self.worker._clean_queue([self.battle_1_record], [self.battle_2_record])
        self.assertEqual(self.worker.arena_queue, {})
        self.assertEqual(Battle1x1.objects.all().count(), 1)


    def test_initiate_battle(self):

        self.assertEqual(SupervisorTask.objects.all().count(), 0)

        self.worker._initiate_battle(self.battle_1_record, self.battle_2_record)

        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle_1.id).enemy_id, self.account_2.id)
        self.assertEqual(Battle1x1Prototype.get_by_id(self.battle_2.id).enemy_id, self.account_1.id)

        self.assertEqual(SupervisorTask.objects.all().count(), 1)
