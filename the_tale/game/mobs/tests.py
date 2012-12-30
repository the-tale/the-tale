# coding: utf-8
import mock

from django.test import TestCase

from game.mobs.storage import MobsDatabase
from game.mobs.prototypes import MobPrototype
from game.mobs.conf import mobs_settings
from game.mobs.exceptions import MobsException

from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import ITEM_TYPE
from game.map.places.models import TERRAIN
from game.logic import create_test_map
from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype

class MobsDatabaseTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)


    def test_load_real_data(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.MOBS_STORAGE)

    def test_load_data(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        self.assertEqual(len(storage.data), 8)

        self.assertTrue('id' not in storage.data)

        test_mobs = ['deer', 'bandit', 'jackal', 'leech', 'rat', 'scorpion', 'tadpole', 'wolf']

        self.assertEqual(frozenset(test_mobs),  frozenset(storage.data.keys()))


    def test_load_mobs_data(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        bandit = storage.data['bandit']

        self.assertEqual(bandit.level , 1)
        self.assertEqual(bandit.id , u'bandit')
        self.assertEqual(bandit.name , u'бандит')
        self.assertEqual(bandit.normalized_name , u'бандит')
        self.assertEqual(bandit.abilities , frozenset(['hit', 'thick', 'slow', 'extra_strong']))
        self.assertEqual(bandit.terrain , frozenset(['.', 'f']))
        self.assertEqual(bandit.loot , frozenset(['fake_amulet']))
        self.assertEqual(bandit.artifacts , frozenset(['broken_sword', 'decrepit_plate']))

        wolf = storage.data['wolf']
        self.assertEqual(wolf.morph, (u'мн',))


    def test_mob_attributes(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        bandit = MobPrototype(record=storage.data['bandit'], level=1)

        self.assertEqual(bandit.health_cooficient, 1.025)
        self.assertEqual(bandit.initiative, 0.975)
        self.assertEqual(bandit.damage_modifier, 1.05)

    def test_load_duplicates(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)
        self.assertRaises(MobsException, storage.load, mobs_settings.TEST_STORAGE)


    def test_get_available_mobs_list(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        mobs_in_forest = [mob.id for mob in storage.get_available_mobs_list(1, TERRAIN.FOREST)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset(['deer', 'bandit', 'wolf']))

        mobs_in_forest = [mob.id for mob in storage.get_available_mobs_list(0, TERRAIN.FOREST)]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    def test_empty_loot_field(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        self.assertEqual(storage.data['jackal'].artifacts, frozenset())

    def test_mobs_and_loot_integrity(self):
        storage = MobsDatabase.storage()
        loot_storage = ArtifactsDatabase.storage()

        for mob_record in storage.data.values():
            self.assertTrue(mob_record.loot)
            self.assertTrue(mob_record.artifacts)

            for loot_id in mob_record.loot:
                self.assertTrue(loot_id in loot_storage.data)

            for artifact_id in mob_record.artifacts:
                self.assertTrue(artifact_id in loot_storage.data)

    def test_get_loot(self):

        self.hero.model.level = 5

        mob = None

        # min mob level MUST not be equal to hero level
        # since in other case next check has no meaning
        while mob is None or mob.record.level == self.hero.level:
            mob = MobsDatabase.storage().get_random_mob(self.hero)

        self.assertTrue(self.hero.level != mob.record.level)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
            artifact = mob.get_loot()
            self.assertEqual(artifact.level, 5)
            self.assertTrue(artifact.type != ITEM_TYPE.USELESS)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1):
            artifact = mob.get_loot()
            self.assertEqual(artifact.level, mob.record.level)
            self.assertEqual(artifact.type, ITEM_TYPE.USELESS)
