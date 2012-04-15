# coding: utf-8

from django.test import TestCase

from .storage import MobsDatabase
from .conf import mobs_settings
from .exceptions import MobsException

class MobsDatabaseTest(TestCase):

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
        self.assertEqual(bandit.speed , 1)
        self.assertEqual(bandit.health , 0.8)
        self.assertEqual(bandit.damage , 1)
        self.assertEqual(bandit.damage_dispersion , 0.2)
        self.assertEqual(bandit.abilities , frozenset(['hit']))
        self.assertEqual(bandit.terrain , frozenset(['grass', 'forest']))
        self.assertEqual(bandit.loot , frozenset(['fake_amulet']))
        self.assertEqual(bandit.artifacts , frozenset(['broken_sword', 'decrepit_plate']))


    def test_load_duplicates(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)
        self.assertRaises(MobsException, storage.load, mobs_settings.TEST_STORAGE)


    def test_get_available_mobs_list(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        mobs_in_forest = [mob.id for mob in storage.get_available_mobs_list(1, 'forest')]
        self.assertEqual(frozenset(mobs_in_forest), frozenset(['deer', 'bandit', 'wolf']))

        mobs_in_forest = [mob.id for mob in storage.get_available_mobs_list(0, 'forest')]
        self.assertEqual(frozenset(mobs_in_forest), frozenset())


    def test_empty_loot_field(self):
        storage = MobsDatabase()
        storage.load(mobs_settings.TEST_STORAGE)

        self.assertEqual(storage.data['jackal'].artifacts, frozenset())
