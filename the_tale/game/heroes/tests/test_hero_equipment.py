# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.balance.power import Power
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT


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
        self.assertTrue(self.hero.power.physic > old_power.physic or
                        self.hero.power.magic > old_power.magic)
        self.assertTrue(artifact.power == Power(1, 0) or
                        artifact.power == Power(0, 1))
        self.assertTrue(self.hero.equipment.updated)


    def test_sharp_artifact_when_all_artifacts_has_max_power(self):
        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level)

        for artifact in self.hero.equipment.equipment.values():
            artifact.power = max_power.clone()

        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()

        self.assertTrue(self.hero.power.physic > old_power.physic or
                        self.hero.power.magic > old_power.magic)

        self.assertTrue(artifact.power == max_power + Power(1, 0) or
                        artifact.power == max_power + Power(0, 1))
        self.assertTrue(self.hero.equipment.updated)

    def test_sharp_preferences(self):
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.sharp_artifact()
        self.assertTrue(artifact.type.is_MAIN_HAND)

    def test_sharp_preferences_with_max_power(self):
        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level)

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.equipment.get(EQUIPMENT_SLOT.HAND_PRIMARY)
        artifact.power = max_power

        artifact = self.hero.sharp_artifact()
        self.assertFalse(artifact.type.is_MAIN_HAND)

    def test_buy_artifact_and_not_equip(self):
        self.hero.equipment.serialize()
        old_equipment = self.hero._model.equipment

        self.hero.bag.serialize()
        old_bag = self.hero._model.bag

        self.hero.buy_artifact(equip=False, better=False, with_prefered_slot=False)

        self.hero.equipment.serialize()
        self.assertEqual(old_equipment, self.hero._model.equipment)

        self.hero.bag.serialize()
        self.assertNotEqual(old_bag, self.hero._model.bag)


    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_canditates(), (None, None, None))

        #equip artefact in empty slot
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)

        equip_slot = artifact.type.equipment_slot
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
        new_artifact.power = artifact.power + Power(1, 1)
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
        artifact.power = old_artifact.power + Power(1, 1)
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

        self.assertTrue(old_hero_power.magic < self.hero.power.magic or
                        old_hero_power.physic < self.hero.power.physic)

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

        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level)

        for i in xrange(100):
            old_artifact = self.hero.equipment.get(EQUIPMENT_SLOT.PLATE)
            self.hero.buy_artifact(better=False, with_prefered_slot=True, equip=True)
            self.assertTrue(self.hero.equipment.get(EQUIPMENT_SLOT.PLATE).preference_rating(distribution) >= old_artifact.preference_rating(distribution))

    def test_compare_drop__none(self):
        distribution = self.hero.preferences.archetype.power_distribution

        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666)
        self.assertTrue(self.hero.bag._compare_drop(distribution, None, loot))
        self.assertFalse(self.hero.bag._compare_drop(distribution, loot, None))

    def test_compare_drop__useless_and_useless(self):
        distribution = self.hero.preferences.archetype.power_distribution

        loot_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 2)
        loot_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 1)
        self.assertTrue(self.hero.bag._compare_drop(distribution, loot_1, loot_2))

    def test_compare_drop__artifact_and_useless(self):
        distribution = self.hero.preferences.archetype.power_distribution

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666)
        self.assertTrue(self.hero.bag._compare_drop(distribution, artifact, loot))

    def test_compare_drop__useless_and_artifact(self):
        distribution = self.hero.preferences.archetype.power_distribution

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666)
        self.assertFalse(self.hero.bag._compare_drop(distribution, loot, artifact))

    def test_compare_drop__artifact_and_artifact(self):
        artifact_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)
        artifact_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1)

        artifact_2.power = Power(1, 1)
        artifact_1.power = Power(2, 2)

        distribution = self.hero.preferences.archetype.power_distribution

        self.assertTrue(self.hero.bag._compare_drop(distribution, artifact_1, artifact_2))
        self.assertFalse(self.hero.bag._compare_drop(distribution, artifact_2, artifact_1))


    def test_drop_cheapest_item__no_items(self):
        self.assertEqual(self.hero.bag.occupation, 0)

        distribution = self.hero.preferences.archetype.power_distribution

        dropped_item = self.hero.bag.drop_cheapest_item(distribution)

        self.assertEqual(dropped_item, None)


    def test_drop_cheapest_item(self):
        artifact_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        artifact_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)

        artifact_1.power = Power(200, 200)
        artifact_2.power = Power(1, 1)

        self.hero.bag.put_artifact(artifact_1)
        self.hero.bag.put_artifact(artifact_2)

        distribution = self.hero.preferences.archetype.power_distribution

        self.assertEqual(self.hero.bag.occupation, 2)

        dropped_item = self.hero.bag.drop_cheapest_item(distribution)

        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertEqual(dropped_item.id, artifact_2.id)

        self.assertEqual(self.hero.bag.values()[0].id, artifact_1.id)
