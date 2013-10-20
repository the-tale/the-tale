# coding: utf-8
import mock
import random

from textgen.words import Noun

from dext.utils import s11n

from common.utils import testcase

from accounts.logic import register_user

from game.logic import create_test_map, DEFAULT_HERO_EQUIPMENT

from game.heroes.prototypes import HeroPrototype

from game.artifacts.exceptions import ArtifactsException
from game.artifacts.storage import artifacts_storage
from game.artifacts.prototypes import ArtifactRecordPrototype, ArtifactPrototype
from game.artifacts.models import ARTIFACT_RECORD_STATE, RARITY_TYPE
from game.artifacts.forms import ModerateArtifactRecordForm
from game.artifacts.relations import ARTIFACT_TYPE


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

        artifacts_storage.sync(force=True)

    def test_serialization(self):
        artifact = artifacts_storage.all()[0].create_artifact(level=6, power=100)
        self.assertEqual(artifact, ArtifactPrototype.deserialize(artifact.serialize()))

    def test_deserialization_of_disabled_artifact(self):
        artifact_record = artifacts_storage.all()[0]
        artifact = artifact_record.create_artifact(level=7)

        data = artifact.serialize()

        artifact_record.state = ARTIFACT_RECORD_STATE.DISABLED
        artifact_record.save()

        artifact_2 = ArtifactPrototype.deserialize(data)

        self.assertNotEqual(artifact.id, artifact_2.id)


    def test_load_data(self):
        self.assertEqual(len(artifacts_storage.all()), 12) # see create_test_map
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
                                       level=1,
                                       name='bandit loot',
                                       description='bandit loot description',
                                       type_=ARTIFACT_TYPE.HELMET,
                                       rarity=RARITY_TYPE.NORMAL)

        loot = ArtifactPrototype(record=artifacts_storage.get_by_uuid('bandit_loot'), level=1)

        self.assertFalse(loot.is_useless)


    def test_artifacts(self):
        self.assertEqual(set(a.uuid for a in  artifacts_storage.artifacts),
                         set(['helmet_1', 'plate_1', 'boots_1'] + DEFAULT_HERO_EQUIPMENT._ALL))

    def test_loot(self):
        self.assertEqual(set(a.uuid for a in artifacts_storage.loot), set(['loot_1', 'loot_2', 'loot_3', 'letter']))

    def test_artifacts_for_type(self):
        self.assertEqual(set([ a.uuid for a in artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.HELMET, ARTIFACT_TYPE.BOOTS])]), set(['helmet_1', 'boots_1', 'default_boots']))
        self.assertEqual(set([ a.uuid for a in artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.PLATE])]), set(['plate_1', 'default_plate']))

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
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
                self.assertTrue(artifact.id in ['helmet_1', 'plate_1', 'boots_1'] + DEFAULT_HERO_EQUIPMENT._ALL)

        with mock.patch('game.artifacts.prototypes.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                              RARITY_TYPE.RARE: 1,
                                                                              RARITY_TYPE.EPIC: 0 }):
            for i in xrange(100):
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
                self.assertTrue(artifact.id in ['helmet_2', 'plate_2', 'boots_2'])

        with mock.patch('game.artifacts.prototypes.RARITY_TYPE_2_PRIORITY', { RARITY_TYPE.NORMAL: 0,
                                                                              RARITY_TYPE.RARE: 0,
                                                                              RARITY_TYPE.EPIC: 1 }):
            for i in xrange(100):
                artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
                self.assertTrue(artifact.id in ['helmet_3', 'plate_3', 'boots_3'])

    def test_generate_artifact(self):
        from game.mobs.prototypes import MobPrototype, MobRecordPrototype
        from game.mobs.models import MOB_RECORD_STATE

        self.hero._model.level = 5

        mob_record = MobRecordPrototype.create_random(uuid='bandit', level=2, state=MOB_RECORD_STATE.ENABLED)
        mob = MobPrototype(record=mob_record, level=3)
        artifact_1 = ArtifactRecordPrototype.create_random('bandit_loot', mob=mob_record, type_=ARTIFACT_TYPE.USELESS, state=ARTIFACT_RECORD_STATE.ENABLED)
        artifact_2 = ArtifactRecordPrototype.create_random('bandit_artifact', mob=mob_record, type_=ARTIFACT_TYPE.HELMET, state=ARTIFACT_RECORD_STATE.ENABLED)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
            artifact = artifacts_storage.generate_loot(mob)
            self.assertEqual(artifact.level, mob.level)
            self.assertFalse(artifact.type._is_USELESS)
            self.assertEqual(artifact_2.id, artifact.record.id)

        with mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1):
            artifact = artifacts_storage.generate_loot(mob)
            self.assertEqual(artifact.level, mob.record.level)
            self.assertTrue(artifact.type._is_USELESS)
            self.assertEqual(artifact_1.id, artifact.record.id)

    def test_disabled_artifacts(self):
        loot = ArtifactRecordPrototype.create_random('disabled_loot', type_=ARTIFACT_TYPE.USELESS, state=ARTIFACT_RECORD_STATE.DISABLED)
        artifact = ArtifactRecordPrototype.create_random('disabled_artifact', type_=ARTIFACT_TYPE.HELMET, state=ARTIFACT_RECORD_STATE.DISABLED)

        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(a.uuid for a in artifacts_storage.artifacts))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(a.uuid for a in artifacts_storage.loot))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.USELESS, ARTIFACT_TYPE.HELMET])))

        self.assertEqual(artifacts_storage.generate_artifact_from_list([loot, artifact], level=1), None)

    def test_change_uuid(self):
        loot = ArtifactRecordPrototype.create_random('some_loot', type_=ARTIFACT_TYPE.USELESS, state=ARTIFACT_RECORD_STATE.DISABLED)

        form = ModerateArtifactRecordForm({'level': '1',
                                           'type': ARTIFACT_TYPE.USELESS,
                                           'rarity': RARITY_TYPE.NORMAL,
                                           'uuid': 'new_uid',
                                           'name_forms': s11n.to_json(Noun.fast_construct('artifact name').serialize())})
        self.assertTrue(form.is_valid())
        self.assertEqual(loot.uuid, artifacts_storage.get_by_uuid(loot.uuid).uuid)

        loot.update_by_moderator(form)

        self.assertEqual(loot.uuid, 'new_uid')
        self.assertEqual(loot.uuid, artifacts_storage.get_by_uuid(loot.uuid).uuid)


    def test_change_uuid_of_default_equipment(self):
        form = ModerateArtifactRecordForm({'level': '1',
                                           'type': ARTIFACT_TYPE.USELESS,
                                           'rarity': RARITY_TYPE.NORMAL,
                                           'uuid': 'artifact_uuid',
                                           'name_forms': s11n.to_json(Noun(normalized='artifact name',
                                                                           forms=['artifact name'] * Noun.FORMS_NUMBER,
                                                                           properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())

        default_artifact = artifacts_storage.get_by_uuid(random.choice(DEFAULT_HERO_EQUIPMENT._ALL))

        self.assertRaises(ArtifactsException, default_artifact.update_by_moderator, form)


    def test_disable_default_equipment(self):
        form = ModerateArtifactRecordForm({'level': '1',
                                           'type': ARTIFACT_TYPE.USELESS,
                                           'rarity': RARITY_TYPE.NORMAL,
                                           'uuid': 'artifact_uuid',
                                           'name_forms': s11n.to_json(Noun(normalized='artifact name',
                                                                           forms=['artifact name'] * Noun.FORMS_NUMBER,
                                                                           properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())

        default_artifact = artifacts_storage.get_by_uuid(random.choice(DEFAULT_HERO_EQUIPMENT._ALL))

        self.assertRaises(ArtifactsException, default_artifact.update_by_moderator, form)
