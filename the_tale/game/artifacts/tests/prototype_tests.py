# coding: utf-8
import mock

from django.test import TestCase

from accounts.logic import register_user

from game.logic import create_test_map, DEFAULT_HERO_EQUIPMENT

from game.heroes.prototypes import HeroPrototype

from game.artifacts.storage import artifacts_storage
from game.artifacts.prototypes import ArtifactRecordPrototype, ArtifactPrototype
from game.artifacts.models import ARTIFACT_RECORD_STATE, RARITY_TYPE, ARTIFACT_TYPE

class PrototypeTests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

        artifacts_storage.sync(force=True)


    def test_load_data(self):
        self.assertEqual(len(artifacts_storage.all()), 11) # see create_test_map
        self.assertFalse(artifacts_storage.has_artifact('wrong_id'))
        self.assertTrue(artifacts_storage.has_artifact('loot_1'))
        self.assertTrue(artifacts_storage.has_artifact('loot_2'))
        self.assertTrue(artifacts_storage.has_artifact('loot_3'))
        self.assertTrue(artifacts_storage.has_artifact('helmet_1'))
        self.assertTrue(artifacts_storage.has_artifact('plate_1'))
        self.assertTrue(artifacts_storage.has_artifact('boots_1'))

    def test_storage_version_update_on_create(self):
        old_version = artifacts_storage.version
        ArtifactRecordPrototype.create_random(uuid='bandit_loot')
        self.assertNotEqual(old_version, artifacts_storage.version)

    def test_storage_version_update_on_save(self):
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot')
        old_version = artifacts_storage.version
        artifact.save()
        self.assertNotEqual(old_version, artifacts_storage.version)

    def test_artifacts_attributes(self):
        ArtifactRecordPrototype.create(uuid='bandit_loot',
                                       min_level=1,
                                       max_level=6,
                                       name='bandit loot',
                                       description='bandit loot description',
                                       type_=ARTIFACT_TYPE.HELMET,
                                       rarity=RARITY_TYPE.NORMAL)

        loot = ArtifactPrototype(record=artifacts_storage.get_by_uuid('bandit_loot'), level=1)

        self.assertFalse(loot.is_useless)


    def test_artifacts_ids(self):
        self.assertEqual(set(artifacts_storage.artifacts_ids),
                         set(['helmet_1', 'plate_1', 'boots_1'] + DEFAULT_HERO_EQUIPMENT._ALL))

    def test_loot_ids(self):
        self.assertEqual(set(artifacts_storage.loot_ids),
                         set(['loot_1', 'loot_2', 'loot_3']))

    def test_artifacts_for_equip_type(self):
        self.assertEqual(set(artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.HELMET, ARTIFACT_TYPE.BOOTS])), set(['helmet_1', 'boots_1', 'default_boots']))
        self.assertEqual(set(artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.PLATE])), set(['plate_1', 'default_plate']))

    def test_generate_artifact_from_list(self):

        ArtifactRecordPrototype.create_random('helmet_2', type_=ARTIFACT_TYPE.HELMET, rarity=RARITY_TYPE.RARE)
        ArtifactRecordPrototype.create_random('plate_2', type_=ARTIFACT_TYPE.PLATE, rarity=RARITY_TYPE.RARE)
        ArtifactRecordPrototype.create_random('boots_2', type_=ARTIFACT_TYPE.BOOTS, rarity=RARITY_TYPE.RARE)

        ArtifactRecordPrototype.create_random('helmet_3', type_=ARTIFACT_TYPE.HELMET, rarity=RARITY_TYPE.EPIC)
        ArtifactRecordPrototype.create_random('plate_3', type_=ARTIFACT_TYPE.PLATE, rarity=RARITY_TYPE.EPIC)
        ArtifactRecordPrototype.create_random('boots_3', type_=ARTIFACT_TYPE.BOOTS, rarity=RARITY_TYPE.EPIC)

        with mock.patch('game.artifacts.prototypes.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 1,
                                                                              RARITY_TYPE.RARE: 0,
                                                                              RARITY_TYPE.EPIC: 0 }):
            for i in xrange(100):
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['helmet_1', 'plate_1', 'boots_1'] + DEFAULT_HERO_EQUIPMENT._ALL)

        with mock.patch('game.artifacts.prototypes.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                              RARITY_TYPE.RARE: 1,
                                                                              RARITY_TYPE.EPIC: 0 }):
            for i in xrange(100):
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['helmet_2', 'plate_2', 'boots_2'])

        with mock.patch('game.artifacts.prototypes.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                              RARITY_TYPE.RARE: 0,
                                                                              RARITY_TYPE.EPIC: 1 }):
            for i in xrange(100):
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_ids, 1)
                self.assertTrue(artifact.id in ['helmet_3', 'plate_3', 'boots_3'])

    def test_generate_artifact(self):

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
            artifact = artifacts_storage.generate_loot(artifacts_storage.artifacts_ids, artifacts_storage.loot_ids, artifact_level=7, loot_level=3)
            self.assertEqual(artifact.level, 7)
            self.assertFalse(artifact.type.is_useless)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1):
            artifact = artifacts_storage.generate_loot(artifacts_storage.artifacts_ids, artifacts_storage.loot_ids, artifact_level=7, loot_level=3)
            self.assertEqual(artifact.level, 3)
            self.assertTrue(artifact.type.is_useless)

    def test_disabled_artifacts(self):
        ArtifactRecordPrototype.create_random('disabled_loot', type_=ARTIFACT_TYPE.USELESS, state=ARTIFACT_RECORD_STATE.DISABLED)
        ArtifactRecordPrototype.create_random('disabled_artifact', type_=ARTIFACT_TYPE.HELMET, state=ARTIFACT_RECORD_STATE.DISABLED)

        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(artifacts_storage.artifacts_ids))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(artifacts_storage.loot_ids))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.USELESS, ARTIFACT_TYPE.HELMET])))

        self.assertEqual(artifacts_storage.generate_artifact_from_list(['disabled_loot', 'disabled_artifact'], level=1), None)
