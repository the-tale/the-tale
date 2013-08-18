# coding: utf-8

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.artifacts.storage import artifacts_storage

from game.balance import formulas as f
from game.logic_storage import LogicStorage

from game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT


class HeroEquipmentTests(TestCase):

    def setUp(self):
        super(HeroEquipmentTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]
        self.hero._model.level = PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        self.hero.save()

    def test_sharp_artifact(self):
        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()
        self.assertEqual(self.hero.power, old_power+1)
        self.assertEqual(artifact.power, 1)
        self.assertTrue(self.hero.equipment.updated)


    def test_sharp_artifact_when_all_artifacts_has_max_power(self):
        min_power, max_power = f.power_to_artifact_interval(self.hero.level)

        for artifact in self.hero.equipment.equipment.values():
            artifact.power = max_power

        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()
        self.assertEqual(self.hero.power, old_power+1)
        self.assertEqual(artifact.power, max_power + 1)
        self.assertTrue(self.hero.equipment.updated)

    def test_sharp_preferences(self):
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.sharp_artifact()
        self.assertTrue(artifact.type.is_main_hand)

    def test_sharp_preferences_with_max_power(self):
        min_power, max_power = f.power_to_artifact_interval(self.hero.level)

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.equipment.get(EQUIPMENT_SLOT.HAND_PRIMARY)
        artifact.power = max_power

        artifact = self.hero.sharp_artifact()
        self.assertFalse(artifact.type.is_main_hand)

    def test_buy_artifact_and_not_equip(self):
        old_equipment = self.hero.equipment.serialize()
        old_bag = self.hero.bag.serialize()
        self.hero.buy_artifact(equip=False, better=False, with_prefered_slot=False)
        self.assertEqual(old_equipment, self.hero.equipment.serialize())
        self.assertNotEqual(old_bag, self.hero.bag.serialize())


    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_canditates(), (None, None, None))

        #equip artefact in empty slot
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)

        equip_slot = EQUIPMENT_SLOT._index_artifact_type[artifact.type.value]
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
        new_artifact = artifacts_storage.generate_artifact_from_list([artifact.record], self.hero.level)
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

        self.storage._test_save()

    def test_get_equip_canditates__ignore_favorite_item_slot(self):
        self.assertTrue(self.hero.bag.is_empty)
        self.assertTrue(self.hero.equipment.get(EQUIPMENT_SLOT.HAND_PRIMARY))
        self.assertEqual(self.hero.preferences.favorite_item, None)

        old_artifact = self.hero.equipment.get(EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_for_type([EQUIPMENT_SLOT.HAND_PRIMARY.artifact_type]), self.hero.level)
        artifact.power = old_artifact.power + 1
        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertEqual(slot, EQUIPMENT_SLOT.HAND_PRIMARY)
        self.assertEqual(unequipped, old_artifact)
        self.assertEqual(equipped, artifact)

        self.hero.preferences.set_favorite_item(EQUIPMENT_SLOT.HAND_PRIMARY)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertEqual(slot, None)
        self.assertEqual(unequipped, None)
        self.assertEqual(equipped, None)


    def test_randomize_equip__working(self):
        self.hero.randomize_equip()

        old_hero_power = self.hero.power

        self.hero._model.level = 50

        self.hero.randomize_equip()

        self.assertTrue(old_hero_power < self.hero.power)

    def check_buy_artifact_choices(self, equip, with_prefered_slot, prefered_slot=None, favorite_slot=None, expected_choices_ids=frozenset()):
        self.hero._model.level = 666
        self.hero.preferences.set_equipment_slot(prefered_slot)
        self.hero.preferences.set_favorite_item(favorite_slot)

        choices = self.hero.buy_artifact_choices(equip=equip, with_prefered_slot=with_prefered_slot)

        self.assertEqual(set(choice.id for choice in choices), set(expected_choices_ids))

    def test_buy_artifact_choices__no_preferences(self):
        expected_choices_ids = set(artifact.id for artifact in artifacts_storage.artifacts)

        self.check_buy_artifact_choices(equip=False, with_prefered_slot=False, expected_choices_ids=expected_choices_ids)
        self.check_buy_artifact_choices(equip=False, with_prefered_slot=True, expected_choices_ids=expected_choices_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=False, expected_choices_ids=expected_choices_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=True, expected_choices_ids=expected_choices_ids)

    def test_buy_artifact_choices__exclude_favorite_slot(self):
        favorite_slot = EQUIPMENT_SLOT.PLATE

        artifacts_for_type = artifacts_storage.artifacts_for_type([favorite_slot.artifact_type])

        self.assertTrue(artifacts_for_type)

        all_choices_ids = set(artifact.id for artifact in artifacts_storage.artifacts)

        expected_choices_ids = all_choices_ids - set(artifact.id for artifact in artifacts_for_type)

        self.check_buy_artifact_choices(equip=False, with_prefered_slot=False, favorite_slot=favorite_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=False, with_prefered_slot=True, favorite_slot=favorite_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=False, favorite_slot=favorite_slot, expected_choices_ids=expected_choices_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=True, favorite_slot=favorite_slot, expected_choices_ids=expected_choices_ids)

    def test_buy_artifact_choices__with_prefered_slot(self):
        prefered_slot = EQUIPMENT_SLOT.PLATE

        artifacts_for_type = [a.id for a in artifacts_storage.artifacts_for_type([prefered_slot.artifact_type])]

        self.assertTrue(artifacts_for_type)

        all_choices_ids = set(artifact.id for artifact in artifacts_storage.artifacts)

        self.check_buy_artifact_choices(equip=False, with_prefered_slot=False, prefered_slot=prefered_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=False, with_prefered_slot=True, prefered_slot=prefered_slot, expected_choices_ids=artifacts_for_type)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=False, prefered_slot=prefered_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=True, prefered_slot=prefered_slot, expected_choices_ids=artifacts_for_type)

    def test_buy_artifact_choices__with_prefered_slot_and_favorite_slot(self):
        all_choices_ids = set(artifact.id for artifact in artifacts_storage.artifacts)

        prefered_slot = EQUIPMENT_SLOT.PLATE

        prefered_artifacts_ids = [a.id for a in artifacts_storage.artifacts_for_type([prefered_slot.artifact_type])]

        self.assertTrue(prefered_artifacts_ids)

        favorite_slot = EQUIPMENT_SLOT.HAND_PRIMARY

        favorite_artifacts_ids = set(a.id for a in artifacts_storage.artifacts_for_type([favorite_slot.artifact_type]))

        self.assertTrue(favorite_artifacts_ids)

        without_favorites_ids = all_choices_ids - set(favorite_artifacts_ids)

        self.assertTrue(favorite_artifacts_ids)

        self.check_buy_artifact_choices(equip=False, with_prefered_slot=False, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=False, with_prefered_slot=True, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=prefered_artifacts_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=False, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=without_favorites_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=True, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=prefered_artifacts_ids)


    def test_buy_artifact_choices__equal_prefered_slot_and_favorite_slot(self):
        all_choices_ids = set(artifact.id for artifact in artifacts_storage.artifacts)

        prefered_slot = EQUIPMENT_SLOT.PLATE
        favorite_slot = EQUIPMENT_SLOT.PLATE

        artifacts_ids = [a.id for a in artifacts_storage.artifacts_for_type([prefered_slot.artifact_type])]

        self.assertTrue(artifacts_ids)

        without_favorites_ids = all_choices_ids - set(artifacts_ids)

        self.check_buy_artifact_choices(equip=False, with_prefered_slot=False, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=all_choices_ids)
        self.check_buy_artifact_choices(equip=False, with_prefered_slot=True, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=artifacts_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=False, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=without_favorites_ids)
        self.check_buy_artifact_choices(equip=True, with_prefered_slot=True, prefered_slot=prefered_slot, favorite_slot=favorite_slot, expected_choices_ids=without_favorites_ids)


    def test_buy_artifact__only_better_for_prefered_slot(self):
        self.hero._model.level = 666
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)

        # just set any artifact
        self.hero.buy_artifact(better=False, with_prefered_slot=True, equip=True)

        for i in xrange(100):
            old_artifact = self.hero.equipment.get(EQUIPMENT_SLOT.PLATE)
            self.hero.buy_artifact(better=False, with_prefered_slot=True, equip=True)
            self.assertTrue(self.hero.equipment.get(EQUIPMENT_SLOT.PLATE).power >= old_artifact.power)
