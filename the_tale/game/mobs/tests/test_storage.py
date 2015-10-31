# coding: utf-8
import collections

import mock

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.logic import create_test_map
from the_tale.game import relations as game_relations

from the_tale.game.map import relations as map_relations
from the_tale.game.actions import relations as actions_relations

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.relations import MOB_RECORD_STATE
from the_tale.game.mobs.prototypes import MobRecordPrototype


class MobsStorageTests(testcase.TestCase):

    def setUp(self):
        super(MobsStorageTests, self).setUp()
        create_test_map()

        self.mob_1, self.mob_2, self.mob_3 = mobs_storage.all()

        self.mob_1.type = game_relations.BEING_TYPE.CIVILIZED
        self.mob_1.save()

        self.mob_2.type = game_relations.BEING_TYPE.CIVILIZED
        self.mob_2.is_mercenary = False
        self.mob_2.save()

        self.mob_3.type = game_relations.BEING_TYPE.CIVILIZED
        self.mob_3.save()

        self.bandit = MobRecordPrototype.create(uuid='bandit',
                                                level=1,
                                                utg_name=names.generator.get_test_name(name='bandint'),
                                                description='description',
                                                abilities=['hit'],
                                                terrains=[map_relations.TERRAIN.PLANE_SAND],
                                                type=game_relations.BEING_TYPE.CIVILIZED,
                                                state=MOB_RECORD_STATE.ENABLED)
        self.bandint_wrong = MobRecordPrototype.create(uuid='bandit_wrong',
                                                       level=1,
                                                       utg_name=names.generator.get_test_name(name='bandit_wrong'),
                                                       description='bandit_wrong description',
                                                       abilities=['hit'],
                                                       terrains=[map_relations.TERRAIN.PLANE_SAND],
                                                       type=game_relations.BEING_TYPE.CIVILIZED,
                                                       state=MOB_RECORD_STATE.DISABLED)


    def test_initialize(self):
        self.assertEqual(len(mobs_storage.all()), 5)
        self.assertEqual(mobs_storage.mobs_number, 5)
        self.assertEqual(sum(mobs_storage._types_count.itervalues()), 5)
        self.assertTrue(mobs_storage.mob_type_fraction(game_relations.BEING_TYPE.CIVILIZED) > 2.0 / 5)

    def test_get_available_mobs_list(self):
        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    def test_get_available_mobs_list__mercenary__true(self):

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    def test_get_available_mobs_list__mercenary__false(self):
        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    @mock.patch('the_tale.game.mobs.storage.MobsStorage.get_available_mobs_list', mock.Mock(return_value=[]))
    def test_get_random_mob__no_mob(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        self.assertEqual(mobs_storage.get_random_mob(hero), None)


    def test_get_random_mob__boss(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        boss = mobs_storage.get_random_mob(hero, is_boss=True)

        self.assertTrue(boss.is_boss)

        normal_mob = boss.record.create_mob(hero)

        self.assertFalse(normal_mob.is_boss)

        self.assertTrue(boss.max_health > normal_mob.max_health)

    def test_get_random_mob__action_type(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        action_type = actions_relations.ACTION_TYPE.random()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.ui_type', action_type):
            mob = mobs_storage.get_random_mob(hero)

        self.assertEqual(mob.action_type, action_type)

    def test_get_random_mob__terrain(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        terrain = map_relations.TERRAIN.random()

        with mock.patch('the_tale.game.heroes.position.Position.get_terrain', lambda h: terrain):
            mob = mobs_storage.get_random_mob(hero)

        self.assertEqual(mob.terrain, terrain)

    def test_choose_mob__when_actions(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        MobRecordPrototype.create_random('action_1', global_action_probability=0.25)
        MobRecordPrototype.create_random('action_2', global_action_probability=0.10)

        counter = collections.Counter([mobs_storage.get_random_mob(hero).id for i in xrange(1000)])

        non_actions_count = sum(count for uuid, count in counter.iteritems() if uuid not in ('action_1', 'action_2'))

        self.assertTrue(counter['action_2'] < counter['action_1'] < non_actions_count)


    def test_choose_mob__when_actions__total_actions(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        MobRecordPrototype.create_random('action_1', global_action_probability=0.66)
        MobRecordPrototype.create_random('action_2', global_action_probability=0.66)

        counter = collections.Counter([mobs_storage.get_random_mob(hero).id for i in xrange(10000)])

        self.assertEqual(sum([count for uuid, count in counter.iteritems() if uuid not in ('action_1', 'action_2')], 0), 0)

        self.assertTrue(abs(counter['action_2'] - counter['action_1']) < 0.2 * counter['action_2'])
