# coding: utf-8

from django.test import TestCase

from accounts.logic import register_user

from game.logic import create_test_map

# from game.artifacts.storage import ArtifactsDatabase
# from game.artifacts.conf import ITEM_TYPE
from game.map.places.models import TERRAIN
from game.heroes.prototypes import HeroPrototype

from game.mobs.storage import mobs_storage
from game.mobs.models import MOB_RECORD_STATE
from game.mobs.prototypes import MobPrototype, MobRecordPrototype


class MobsPrototypeTests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

        mobs_storage.sync(force=True)

    def test_load_data(self):
        self.assertEqual(len(mobs_storage.all()), 3) # create_test_map create 3 random mobs
        self.assertFalse(mobs_storage.has_mob('wrong_id'))
        self.assertTrue(mobs_storage.has_mob('mob_1'))
        self.assertTrue(mobs_storage.has_mob('mob_2'))
        self.assertTrue(mobs_storage.has_mob('mob_3'))

    def test_storage_version_update_on_create(self):
        old_version = mobs_storage.version
        MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_storage_version_update_on_save(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        old_version = mobs_storage.version
        mob.save()
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_mob_attributes(self):
        MobRecordPrototype.create(uuid='bandit',
                                  level=1,
                                  name='bandint',
                                  description='bandint',
                                  abilities=['hit', 'thick', 'slow', 'extra_strong'],
                                  terrains=TERRAIN._ALL,
                                  state=MOB_RECORD_STATE.ENABLED)
        mobs_storage.sync(force=True)

        bandit = MobPrototype(record=mobs_storage.get_by_uuid('bandit'), level=1)

        self.assertEqual(bandit.health_cooficient, 1.025)
        self.assertEqual(bandit.initiative, 0.975)
        self.assertEqual(bandit.damage_modifier, 1.05)

    def test_get_available_mobs_list(self):
        MobRecordPrototype.create(uuid='bandit',
                                  level=1,
                                  name='bandint',
                                  description='description',
                                  abilities=['hit'],
                                  terrains=[TERRAIN.PLANE_SAND],
                                  state=MOB_RECORD_STATE.ENABLED)
        MobRecordPrototype.create(uuid='bandit_wrong',
                                  level=1,
                                  name='bandit_wrong',
                                  description='bandit_wrong description',
                                  abilities=['hit'],
                                  terrains=[TERRAIN.PLANE_SAND],
                                  state=MOB_RECORD_STATE.DISABLED)

        mobs_storage.sync(force=True)

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset(['mob_1', 'mob_2', 'mob_3', 'bandit']))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(1, TERRAIN.PLANE_GRASS)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset(['mob_1', 'mob_2', 'mob_3']))

        mobs_in_forest = [mob.uuid for mob in mobs_storage.get_available_mobs_list(0, TERRAIN.PLANE_SAND)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    # def test_empty_loot_field(self):
    #     storage = MobsDatabase()
    #     storage.load(mobs_settings.TEST_STORAGE)

    #     self.assertEqual(storage.data['jackal'].artifacts, frozenset())

    # def test_mobs_and_loot_integrity(self):
    #     storage = MobsDatabase.storage()
    #     loot_storage = ArtifactsDatabase.storage()

    #     for mob_record in storage.data.values():
    #         self.assertTrue(mob_record.loot)
    #         self.assertTrue(mob_record.artifacts)

    #         for loot_id in mob_record.loot:
    #             self.assertTrue(loot_id in loot_storage.data)

    #         for artifact_id in mob_record.artifacts:
    #             self.assertTrue(artifact_id in loot_storage.data)

    # def test_get_loot(self):

    #     self.hero.model.level = 5

    #     mob = None

    #     # min mob level MUST not be equal to hero level
    #     # since in other case next check has no meaning
    #     while mob is None or mob.record.level == self.hero.level:
    #         mob = MobsDatabase.storage().get_random_mob(self.hero)

    #     self.assertTrue(self.hero.level != mob.record.level)

    #     with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
    #         artifact = mob.get_loot()
    #         self.assertEqual(artifact.level, 5)
    #         self.assertTrue(artifact.type != ITEM_TYPE.USELESS)

    #     with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1):
    #         artifact = mob.get_loot()
    #         self.assertEqual(artifact.level, mob.record.level)
    #         self.assertEqual(artifact.type, ITEM_TYPE.USELESS)
