# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.artifacts.storage import ArtifactsDatabase
from game.prototypes import TimePrototype

from game.balance import formulas as f

from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS


class HeroTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.created_at_turn, TimePrototype.get_current_time().turn_number)

    def test_create_time(self):
        time = TimePrototype.get_current_time()
        time.increment_turn()
        time.increment_turn()
        time.increment_turn()
        time.save()

        bundle = create_test_bundle('CreatedAtTurnHeroTest')
        hero = bundle.tests_get_hero()
        self.assertEqual(hero.created_at_turn, TimePrototype.get_current_time().turn_number)

        self.assertTrue(hero.created_at_turn != self.hero.created_at_turn)


    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_canditates(), (None, None, None))

        #equip artefact in empty slot
        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)

        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertTrue(slot)
        self.assertTrue(unequipped is None)
        self.assertEqual(equipped, artifact)

        self.hero.change_equipment(slot, unequipped, equipped)
        self.assertTrue(not self.hero.bag.items())
        self.assertEqual(self.hero.equipment.get(slot), artifact)

        # change artifact
        new_artifact = ArtifactsDatabase.storage().generate_artifact_from_list([artifact.id], self.hero.level)
        new_artifact.power = artifact.power + 1
        self.hero.bag.put_artifact(new_artifact)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertTrue(slot)
        self.assertEqual(unequipped, artifact)
        self.assertEqual(equipped, new_artifact)

        self.hero.change_equipment(slot, unequipped, equipped)
        self.assertEqual(self.hero.bag.items()[0][1], artifact)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.assertEqual(self.hero.equipment.get(slot), new_artifact)

        test_bundle_save(self, self.bundle)


    def test_lvl_up(self):
        self.assertEqual(self.hero.level, 1)

        self.hero.add_experience(f.exp_on_lvl(1)/2)
        self.assertEqual(self.hero.level, 1)

        self.hero.add_experience(f.exp_on_lvl(1))
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.experience, f.exp_on_lvl(1)/2)

        self.hero.add_experience(f.exp_on_lvl(2))
        self.assertEqual(self.hero.level, 3)

        self.hero.add_experience(f.exp_on_lvl(3))
        self.assertEqual(self.hero.level, 4)
        self.assertEqual(self.hero.destiny_points, 1)

        self.hero.add_experience(f.exp_on_lvl(4))
        self.assertEqual(self.hero.level, 5)
        self.assertEqual(self.hero.destiny_points, 2)
