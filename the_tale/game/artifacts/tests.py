# coding: utf-8
import mock

from django.test import TestCase

from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import artifacts_settings, EQUIP_TYPE, ITEM_TYPE, RARITY_TYPE
from game.artifacts.exceptions import ArtifactsException

class ArtifactsDatabaseTest(TestCase):

    def test_load_real_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.ARTIFACTS_STORAGE)
        storage.load(artifacts_settings.LOOT_STORAGE)

    def test_load_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        self.assertEqual(len(storage.data), 11)

        self.assertTrue('id' not in storage.data)

        test_artifacts = ['antlers', 'skin_of_a_wolf', 'dead_tadpole', 'skin_of_a_deer', 'skin_of_jackal', 'decrepit_plate', 'wolfs_fangs', 'broken_sword']

        self.assertTrue(not(set(test_artifacts) - set(storage.data.keys())))


    def test_load_artifacts_data(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        skin_of_a_wolf = storage.data['skin_of_a_wolf']

        self.assertEqual(skin_of_a_wolf.id , u'skin_of_a_wolf')
        self.assertEqual(skin_of_a_wolf.type , ITEM_TYPE.ARMOR)
        self.assertEqual(skin_of_a_wolf.slot , EQUIP_TYPE.SHOULDERS)
        self.assertEqual(skin_of_a_wolf.name , u'шкура волка')
        self.assertEqual(skin_of_a_wolf.morph , ())
        self.assertEqual(skin_of_a_wolf.normalized_name , u'шкура волка')
        self.assertEqual(skin_of_a_wolf.min_lvl , 1)
        self.assertEqual(skin_of_a_wolf.max_lvl , 60)
        self.assertEqual(skin_of_a_wolf.rarity, RARITY_TYPE.NORMAL)

        antlers = storage.data['antlers']
        self.assertEqual(antlers.morph, (u'мн',))

    def test_load_duplicates(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)
        self.assertRaises(ArtifactsException, storage.load, artifacts_settings.TEST_STORAGE)

    def test_generate_artifact_from_list(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        with mock.patch('game.artifacts.storage.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 1,
                                                                        RARITY_TYPE.RARE: 0,
                                                                        RARITY_TYPE.EPIC: 0 }):
            for i in xrange(100):
                artifact = storage.generate_artifact_from_list(storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['antlers', 'skin_of_a_wolf', 'skin_of_jackal', 'broken_sword'])

        with mock.patch('game.artifacts.storage.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                        RARITY_TYPE.RARE: 1,
                                                                        RARITY_TYPE.EPIC: 0 }):
            for i in xrange(100):
                artifact = storage.generate_artifact_from_list(storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['decrepit_plate', 'wolfs_fangs'])

        with mock.patch('game.artifacts.storage.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                        RARITY_TYPE.RARE: 0,
                                                                        RARITY_TYPE.EPIC: 1 }):
            for i in xrange(100):
                artifact = storage.generate_artifact_from_list(storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['dead_tadpole', 'skin_of_a_deer'])

    def test_generate_artifact(self):
        storage = ArtifactsDatabase()
        storage.load(artifacts_settings.TEST_STORAGE)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
            artifact = storage.generate_loot(storage.artifacts_ids, storage.loot_ids, artifact_level=7, loot_level=3)
            self.assertEqual(artifact.level, 7)
            self.assertTrue(artifact.type != ITEM_TYPE.USELESS)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1):
            artifact = storage.generate_loot(storage.artifacts_ids, storage.loot_ids, artifact_level=7, loot_level=3)
            self.assertEqual(artifact.level, 3)
            self.assertEqual(artifact.type, ITEM_TYPE.USELESS)
