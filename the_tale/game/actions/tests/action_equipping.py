# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map
from game.actions.prototypes import ActionEquippingPrototype

from game.artifacts.storage import ArtifactsDatabase
from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS

class ActionEquippingTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('EquippingActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionEquippingPrototype.create(self.action_idl))
        self.action_equipping = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()


    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_equipping.leader, True)


    def test_processed(self):
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)


    def test_equip(self):
        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        artifact.power = 666

        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_equipping)
        self.assertEqual(len(self.hero.bag.items()), 0)

        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.assertEqual(self.hero.equipment.get(equip_slot), artifact)


    def test_switch_artifact(self):
        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        artifact.power = 13
        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.hero.equipment.unequip(equip_slot)
        self.hero.equipment.equip(equip_slot, artifact)

        new_artifact = ArtifactsDatabase.storage().generate_artifact_from_list([artifact.id], self.hero.level+1)
        new_artifact.power = 666

        self.hero.bag.put_artifact(new_artifact)

        self.bundle.process_turn(1)

        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_equipping)

        self.assertEqual(len(self.hero.bag.items()), 1)
        self.assertEqual(self.hero.bag.items()[0][1].power, 13)

        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.assertEqual(self.hero.equipment.get(equip_slot), new_artifact)
        self.assertEqual(self.hero.equipment.get(equip_slot).power, 666)
