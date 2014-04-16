# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.map.relations import TERRAIN

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE
from the_tale.game.mobs.prototypes import MobRecordPrototype


class MobsStorageTests(testcase.TestCase):

    def setUp(self):
        super(MobsStorageTests, self).setUp()
        create_test_map()

        self.mob_1, self.mob_2, self.mob_3 = mobs_storage.all()

        self.mob_1.type = MOB_TYPE.CIVILIZED
        self.mob_1.save()

        self.mob_2.type = MOB_TYPE.BARBARIAN
        self.mob_2.save()

        self.mob_3.type = MOB_TYPE.CIVILIZED
        self.mob_3.save()

        self.bandit = MobRecordPrototype.create(uuid='bandit',
                                                level=1,
                                                name='bandint',
                                                description='description',
                                                abilities=['hit'],
                                                terrains=[TERRAIN.PLANE_SAND],
                                                type=MOB_TYPE.CIVILIZED,
                                                state=MOB_RECORD_STATE.ENABLED)
        self.bandint_wrong = MobRecordPrototype.create(uuid='bandit_wrong',
                                                       level=1,
                                                       name='bandit_wrong',
                                                       description='bandit_wrong description',
                                                       abilities=['hit'],
                                                       terrains=[TERRAIN.PLANE_SAND],
                                                       type=MOB_TYPE.CIVILIZED,
                                                       state=MOB_RECORD_STATE.DISABLED)


    def test_initialize(self):
        self.assertEqual(len(mobs_storage.all()), 5)
        self.assertEqual(mobs_storage.mobs_number, 5)
        self.assertEqual(sum(mobs_storage._types_count.itervalues()), 5)
        self.assertTrue(mobs_storage.mob_type_fraction(MOB_TYPE.CIVILIZED) > 2.0 / 5)

    def test_get_available_mobs_list(self):
        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_GRASS)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    def test_get_available_mobs_list__mercenary__true(self):

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_GRASS, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    def test_get_available_mobs_list__mercenary__false(self):
        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_GRASS, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    @mock.patch('the_tale.game.mobs.storage.MobsStorage.get_available_mobs_list', mock.Mock(return_value=[]))
    def test_get_random_mob__no_mob(self):
        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        hero = HeroPrototype.get_by_account_id(account_id)

        self.assertEqual(mobs_storage.get_random_mob(hero), None)


    def test_get_random_mob__boss(self):
        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        hero = HeroPrototype.get_by_account_id(account_id)

        boss = mobs_storage.get_random_mob(hero, is_boss=True)

        self.assertTrue(boss.is_boss)

        normal_mob = boss.record.create_mob(hero)

        self.assertFalse(normal_mob.is_boss)

        self.assertTrue(boss.max_health > normal_mob.max_health)
