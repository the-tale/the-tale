# coding: utf-8

from unittest import TestCase

from mock import Mock, patch, create_autospec
from the_tale.game.artifacts.relations import RARITY
from the_tale.game.heroes.relations import EQUIPMENT_SLOT


class BaseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        modules = {
            'the_tale.amqp_environment': Mock(),
            'the_tale.linguistics': Mock(),
            'the_tale.linguistics.lexicon': Mock(),
            'the_tale.linguistics.lexicon.dictionary': Mock(),
            'the_tale.game.artifacts.models': Mock(),
        }
        cls.module_patcher = patch.dict('sys.modules', modules)
        cls.module_patcher.start()

        from rels.relations import Column
        with patch.object(Column, 'check_uniqueness_restriction'):
            from the_tale.game.heroes.bag import Bag
            from the_tale.game.heroes.bag import Equipment
            from the_tale.game.artifacts.prototypes import ArtifactPrototype

        cls.ArtifactPrototype = ArtifactPrototype
        cls.Equipment = Equipment
        cls.Bag = Bag

    def setUp(self):
        self.hero = Mock()
        self.bag = self.Bag()
        self.equipment = self.Equipment()
        self.equipment.hero = self.hero
        self.artifacts = [create_autospec(self.ArtifactPrototype) for _ in range(2)]
        for i, artifact in enumerate(self.artifacts):
            artifact.serialize.return_value = {'artifact': i}

    @classmethod
    def tearDownClass(cls):
        cls.module_patcher.stop()


class BagTests(BaseTests):
    def test_create(self):
        self.assertEqual(self.bag.next_uuid, 0)
        self.assertEqual(self.bag.updated, True)
        self.assertEqual(self.bag.bag, {})
        self.assertEqual(self.bag._ui_info, None)
        self.assertEqual(self.bag.occupation, 0)

    def test_serialize(self):
        self.ArtifactPrototype.deserialize = Mock()
        self.ArtifactPrototype.deserialize.side_effect = self.artifacts

        self.bag.put_artifact(self.artifacts[0])
        self.bag.put_artifact(self.artifacts[1])

        self.assertEqual(self.bag.serialize(), self.Bag.deserialize(self.bag.serialize()).serialize())

    def test_put_artifact(self):
        artifact = self.ArtifactPrototype(level=1, rarity=RARITY.NORMAL)

        self.assertEqual(artifact.bag_uuid, None)

        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        self.bag.put_artifact(artifact)

        self.assertEqual(self.bag.occupation, 1)
        self.assertEqual(self.bag.next_uuid, 1)
        self.assertNotEqual(artifact.bag_uuid, None)

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)

        self.assertEqual(self.bag.bag.values(), [artifact])

    def test_pop_artifact(self):
        artifact = self.ArtifactPrototype(level=1, rarity=RARITY.NORMAL)

        self.bag.put_artifact(artifact)

        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        self.bag.pop_artifact(artifact)
        self.assertEqual(self.bag.occupation, 0)

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)

        self.assertEqual(self.bag.bag, {})

    def test_ui_info_cache(self):
        self.bag.put_artifact(self.artifacts[0])
        ui_info = self.bag.ui_info(self.hero)

        self.assertEqual(self.bag._ui_info, ui_info)

        self.bag.mark_updated()

        self.assertEqual(self.bag._ui_info, None)

    def test_mark_updated(self):
        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        self.bag.mark_updated()

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)


class EquipmentTests(BaseTests):
    def test_create(self):
        self.assertEqual(self.equipment.updated, True)
        self.assertEqual(self.equipment.equipment, {})
        self.assertEqual(self.equipment._ui_info, None)

    def test_serialize(self):
        artifact = self.artifacts[0]
        artifact.type.equipment_slot = EQUIPMENT_SLOT.HAND_PRIMARY
        self.ArtifactPrototype.deserialize = Mock()
        self.ArtifactPrototype.deserialize.return_value = artifact

        self.equipment.equip(artifact.type.equipment_slot, artifact)

        self.assertEqual(self.equipment.serialize(),
                         self.Equipment.deserialize(self.equipment.serialize()).serialize())

    def test_ui_info_cache(self):
        artifact = self.artifacts[0]
        artifact.type.equipment_slot = EQUIPMENT_SLOT.HAND_PRIMARY

        self.equipment.equip(artifact.type.equipment_slot, artifact)

        ui_info = self.equipment.ui_info(self.hero)

        self.assertEqual(self.equipment._ui_info, ui_info)

        self.equipment.mark_updated()

        self.assertEqual(self.equipment._ui_info, None)

    def test_mark_updated(self):
        self.equipment.updated = False
        self.equipment._ui_info = 'fake ui info'

        self.equipment.mark_updated()

        self.assertTrue(self.equipment.updated)
        self.assertEqual(self.equipment._ui_info, None)

    def test_get__mark_updated_called(self):
        self.equipment.updated = False

        self.equipment.get(EQUIPMENT_SLOT.PLATE)

        self.assertTrue(self.equipment.updated)

    def test_values__mark_updated_called(self):
        self.equipment.updated = False

        self.equipment.values()

        self.assertTrue(self.equipment.updated)

    def test_quests_cache_reseted(self):
        self.hero.quests.updated = False

        self.equipment.mark_updated()

        self.hero.quests.mark_updated.assert_called_with()
