import collections

from unittest import mock

from tt_logic.beings import relations as beings_relations

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.map import relations as map_relations
from the_tale.game.actions import relations as actions_relations

from the_tale.game.heroes import logic as heroes_logic

from .. import logic
from .. import storage
from .. import relations


class MobsStorageTests(testcase.TestCase):

    def setUp(self):
        super(MobsStorageTests, self).setUp()
        create_test_map()

        self.mob_1, self.mob_2, self.mob_3 = storage.mobs.all()

        self.mob_1.type = beings_relations.TYPE.CIVILIZED
        logic.save_mob_record(self.mob_1)

        self.mob_2.type = beings_relations.TYPE.CIVILIZED
        self.mob_2.is_mercenary = False
        logic.save_mob_record(self.mob_2)

        self.mob_3.type = beings_relations.TYPE.CIVILIZED
        logic.save_mob_record(self.mob_3)

        self.bandit = logic.create_random_mob_record(uuid='bandit',
                                                     level=1,
                                                     utg_name=names.generator().get_test_name(name='bandint'),
                                                     description='description',
                                                     abilities=['hit'],
                                                     terrains=[map_relations.TERRAIN.PLANE_SAND],
                                                     type=beings_relations.TYPE.CIVILIZED,
                                                     state=relations.MOB_RECORD_STATE.ENABLED)
        self.bandint_wrong = logic.create_random_mob_record(uuid='bandit_wrong',
                                                            level=1,
                                                            utg_name=names.generator().get_test_name(name='bandit_wrong'),
                                                            description='bandit_wrong description',
                                                            abilities=['hit'],
                                                            terrains=[map_relations.TERRAIN.PLANE_SAND],
                                                            type=beings_relations.TYPE.CIVILIZED,
                                                            state=relations.MOB_RECORD_STATE.DISABLED)

    def test_initialize(self):
        self.assertEqual(len(storage.mobs.all()), 5)
        self.assertEqual(storage.mobs.mobs_number, 5)
        self.assertEqual(sum(storage.mobs._types_count.values()), 5)
        self.assertTrue(storage.mobs.mob_type_fraction(beings_relations.TYPE.CIVILIZED) > 2.0 / 5)

    def test_get_available_mobs_list(self):
        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    def test_get_available_mobs_list__mercenary__true(self):

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    def test_get_available_mobs_list__mercenary__false(self):
        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(1, map_relations.TERRAIN.PLANE_GRASS, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in storage.mobs.get_available_mobs_list(0, map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    @mock.patch('the_tale.game.mobs.storage.MobsStorage.get_available_mobs_list', mock.Mock(return_value=[]))
    def test_get_random_mob__no_mob(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        self.assertEqual(storage.mobs.get_random_mob(hero), None)


    def test_get_random_mob__boss(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        boss = storage.mobs.get_random_mob(hero, is_boss=True)

        self.assertTrue(boss.is_boss)

        normal_mob = boss.record.create_mob(hero)

        self.assertFalse(normal_mob.is_boss)

        self.assertTrue(boss.max_health > normal_mob.max_health)

    def test_get_random_mob__action_type(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        action_type = actions_relations.ACTION_TYPE.random()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.ui_type', action_type):
            mob = storage.mobs.get_random_mob(hero)

        self.assertEqual(mob.action_type, action_type)

    def test_get_random_mob__terrain(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        terrain = map_relations.TERRAIN.random()

        with mock.patch('the_tale.game.heroes.position.Position.get_terrain', lambda h: terrain):
            mob = storage.mobs.get_random_mob(hero)

        self.assertEqual(mob.terrain, terrain)

    def test_choose_mob__when_actions(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        logic.create_random_mob_record('action_1', global_action_probability=0.25)
        logic.create_random_mob_record('action_2', global_action_probability=0.10)

        counter = collections.Counter([storage.mobs.get_random_mob(hero).id for i in range(1000)])

        non_actions_count = sum(count for uuid, count in counter.items() if uuid not in ('action_1', 'action_2'))

        self.assertTrue(counter['action_2'] < counter['action_1'] < non_actions_count)

    def test_choose_mob__when_actions__total_actions(self):
        account = self.accounts_factory.create_account()
        hero = heroes_logic.load_hero(account_id=account.id)

        logic.create_random_mob_record('action_1', global_action_probability=0.66)
        logic.create_random_mob_record('action_2', global_action_probability=0.66)

        counter = collections.Counter([storage.mobs.get_random_mob(hero).id for i in range(10000)])

        self.assertEqual(sum([count for uuid, count in counter.items() if uuid not in ('action_1', 'action_2')], 0), 0)

        self.assertTrue(abs(counter['action_2'] - counter['action_1']) < 0.2 * counter['action_2'])
