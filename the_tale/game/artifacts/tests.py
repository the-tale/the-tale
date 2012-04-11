# coding: utf-8

from django.test import TestCase

from .storage import ArtifactsDatabase
from .conf import artifacts_settings
from .exceptions import ArtifactsException

class ArtifactsDatabaseTest(TestCase):

    def test_load_real_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.ARTIFACTS_STORAGE)
        storage.load(artifacts_settings.LOOT_STORAGE)

    def test_load_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        self.assertEqual(len(storage.data), 8)

        self.assertTrue('id' not in storage.data)

        test_artifacts = ['antlers', 'skin_of_a_wolf', 'dead_tadpole', 'skin_of_a_deer', 'skin_of_jackal', 'decrepit_plate', 'wolfs_fangs', 'broken_sword']

        self.assertTrue(not(set(test_artifacts) - set(storage.data.keys())))


    def test_load_artifacts_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        skin_of_a_wolf = storage.data['skin_of_a_wolf']

        self.assertEqual(skin_of_a_wolf.id , u'skin_of_a_wolf')
        self.assertEqual(skin_of_a_wolf.type , u'armor')
        self.assertEqual(skin_of_a_wolf.slot , u'shoulders')
        self.assertEqual(skin_of_a_wolf.name , u'шкура волка')
        self.assertEqual(skin_of_a_wolf.normalized_name , u'шкура волка')
        self.assertEqual(skin_of_a_wolf.min_lvl , 1)
        self.assertEqual(skin_of_a_wolf.max_lvl , 6)

    def test_load_duplicates(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)
        self.assertRaises(ArtifactsException, storage.load, artifacts_settings.TEST_STORAGE)
