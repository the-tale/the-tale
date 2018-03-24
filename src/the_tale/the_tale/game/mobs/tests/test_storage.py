
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

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

    def test_initialize(self):
        self.assertEqual(len(storage.mobs.all()), 5)
        self.assertEqual(storage.mobs.mobs_number, 5)
        self.assertEqual(sum(storage.mobs._types_count.values()), 5)
        self.assertTrue(storage.mobs.mob_type_fraction(beings_relations.TYPE.CIVILIZED) > 2.0 / 5)

    def test_get_mobs_choices(self):
        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, mercenary=None, terrain=map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, mercenary=None, terrain=map_relations.TERRAIN.PLANE_GRASS)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_2.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=0, mercenary=None, terrain=map_relations.TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    def test__get_mobs_choices__mercenary__true(self):
        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, terrain=map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid, self.bandit.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, terrain=map_relations.TERRAIN.PLANE_GRASS, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_1.uuid, self.mob_3.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=0, terrain=map_relations.TERRAIN.PLANE_SAND, mercenary=True)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    def test__get_mobs_choices__mercenary__false(self):
        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, terrain=map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=1, terrain=map_relations.TERRAIN.PLANE_GRASS, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset([self.mob_2.uuid]))

        mobs_in_forest = [mob.uuid for mob, priority in storage.mobs._get_mobs_choices(level=0, terrain=map_relations.TERRAIN.PLANE_SAND, mercenary=False)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())

    @mock.patch('the_tale.game.mobs.storage.MobsStorage._get_mobs_choices', mock.Mock(return_value=[]))
    def test_get_random_mob__no_mob(self):
        self.assertEqual(storage.mobs.get_random_mob(self.hero), None)

    def test_get_random_mob__boss(self):
        boss = storage.mobs.get_random_mob(self.hero, is_boss=True)

        self.assertTrue(boss.is_boss)

        normal_mob = boss.record.create_mob(self.hero)

        self.assertFalse(normal_mob.is_boss)

        self.assertTrue(boss.max_health > normal_mob.max_health)

    def test_get_random_mob__action_type(self):
        action_type = actions_relations.ACTION_TYPE.random()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.ui_type', action_type):
            mob = storage.mobs.get_random_mob(self.hero)

        self.assertEqual(mob.action_type, action_type)

    def test_get_random_mob__terrain(self):
        terrain = map_relations.TERRAIN.random()

        with mock.patch('the_tale.game.heroes.position.Position.get_terrain', lambda h: terrain):
            mob = storage.mobs.get_random_mob(self.hero)

        self.assertEqual(mob.terrain, terrain)
