# coding: utf-8
import random

import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts import relations as artifacts_relations

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations

from .. import logic


class _HeroEquipmentTestsBase(TestCase):

    def setUp(self):
        super(_HeroEquipmentTestsBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]
        self.hero.level = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        logic.save_hero(self.hero)


class HeroEquipmentTests(_HeroEquipmentTestsBase):

    def test_put_loot(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            self.hero.put_loot(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL))

    def test_put_loot__bag_is_full(self):
        with self.check_delta(lambda: self.hero.bag.occupation, self.hero.max_bag_size):
            for i in xrange(self.hero.max_bag_size*2):
                self.hero.put_loot(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL))

    @mock.patch('the_tale.game.heroes.objects.Hero.bonus_artifact_power', Power(0, 0))
    def test_put_loot__bonus_power_no_bonus(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = Power(0, 0)
        self.hero.put_loot(artifact)
        self.assertEqual(artifact.power, Power(0, 0))

    @mock.patch('the_tale.game.heroes.objects.Hero.bonus_artifact_power', Power(1, 1))
    def test_put_loot__bonus_power_for_useless(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = Power(0, 0)
        self.hero.put_loot(artifact)
        self.assertEqual(artifact.power, Power(0, 0))

    @mock.patch('the_tale.game.heroes.objects.Hero.bonus_artifact_power', Power(1, 1))
    def test_put_loot__bonus_power_for_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = Power(0, 0)
        self.hero.put_loot(artifact)
        self.assertEqual(artifact.power, Power(1, 1))

    def test_sharp_artifact(self):
        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()
        self.assertTrue(self.hero.power.physic > old_power.physic or
                        self.hero.power.magic > old_power.magic)
        self.assertTrue(artifact.power == Power(2, 1) or
                        artifact.power == Power(1, 2))
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

    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', True)
    def test_sharp_preferences(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.sharp_artifact()
        self.assertTrue(artifact.type.is_MAIN_HAND)

    def test_sharp_preferences_with_max_power(self):
        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level)

        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY)
        artifact.power = max_power

        artifact = self.hero.sharp_artifact()
        self.assertFalse(artifact.type.is_MAIN_HAND)

    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_candidates(), (None, None, None))

        #equip artefact in empty slot
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)

        equip_slot = artifact.type.equipment_slot
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertTrue(slot)
        self.assertTrue(unequipped is None)
        self.assertEqual(equipped, artifact)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.change_equipment(slot, unequipped, equipped)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertTrue(not self.hero.bag.items())
        self.assertEqual(self.hero.equipment.get(slot), artifact)

        # change artifact
        new_artifact = artifacts_storage.generate_artifact_from_list([artifact.record], self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        new_artifact.power = artifact.power + Power(1, 1)
        self.hero.bag.put_artifact(new_artifact)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertTrue(slot)
        self.assertEqual(unequipped, artifact)
        self.assertEqual(equipped, new_artifact)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.change_equipment(slot, unequipped, equipped)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.hero.bag.items()[0][1], artifact)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.assertEqual(self.hero.equipment.get(slot), new_artifact)

        self.storage._test_save()

    def test_get_equip_candidates__ignore_favorite_item_slot(self):
        self.assertTrue(self.hero.bag.is_empty)
        self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY))
        self.assertEqual(self.hero.preferences.favorite_item, None)

        old_artifact = self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_for_type([relations.EQUIPMENT_SLOT.HAND_PRIMARY.artifact_type]),
                                                                 self.hero.level,
                                                                 rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = old_artifact.power + Power(1, 1)
        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertEqual(slot, relations.EQUIPMENT_SLOT.HAND_PRIMARY)
        self.assertEqual(unequipped, old_artifact)
        self.assertEqual(equipped, artifact)

        self.hero.preferences.set_favorite_item(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertEqual(slot, None)
        self.assertEqual(unequipped, None)
        self.assertEqual(equipped, None)


    def test_get_equip_candidates__better_integrity(self):
        self.assertTrue(self.hero.bag.is_empty)
        self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY))

        old_artifact = self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_for_type([relations.EQUIPMENT_SLOT.HAND_PRIMARY.artifact_type]),
                                                                 self.hero.level,
                                                                 rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = old_artifact.power
        artifact.integrity = old_artifact.integrity + 1
        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertEqual(slot, relations.EQUIPMENT_SLOT.HAND_PRIMARY)
        self.assertEqual(unequipped, old_artifact)
        self.assertEqual(equipped, artifact)


    def test_get_equip_candidates__worst_integrity(self):
        self.assertTrue(self.hero.bag.is_empty)
        self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY))

        old_artifact = self.hero.equipment.get(relations.EQUIPMENT_SLOT.HAND_PRIMARY)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts_for_type([relations.EQUIPMENT_SLOT.HAND_PRIMARY.artifact_type]),
                                                                 self.hero.level,
                                                                 rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = old_artifact.power
        artifact.integrity = old_artifact.integrity - 1
        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_candidates()
        self.assertEqual(slot, None)
        self.assertEqual(unequipped, None)
        self.assertEqual(equipped, None)


    def test_randomize_equip__working(self):
        self.hero.randomize_equip()

        old_hero_power = self.hero.power

        self.hero.level = 50

        self.hero.randomize_equip()

        self.assertTrue(old_hero_power.magic < self.hero.power.magic or
                        old_hero_power.physic < self.hero.power.physic)

        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = self.hero.equipment.get(slot)
            if artifact:
                self.assertEqual(artifact.type.equipment_slot, slot)


    def test_compare_drop__none(self):
        distribution = self.hero.preferences.archetype.power_distribution

        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666, rarity=artifacts_relations.RARITY.NORMAL)
        self.assertTrue(self.hero.bag._compare_drop(distribution, None, loot))
        self.assertFalse(self.hero.bag._compare_drop(distribution, loot, None))

    def test_compare_drop__useless_and_useless(self):
        distribution = self.hero.preferences.archetype.power_distribution

        loot_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 2, rarity=artifacts_relations.RARITY.NORMAL)
        loot_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 1, rarity=artifacts_relations.RARITY.NORMAL)
        self.assertTrue(self.hero.bag._compare_drop(distribution, loot_1, loot_2))

    def test_compare_drop__artifact_and_useless(self):
        distribution = self.hero.preferences.archetype.power_distribution

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=artifacts_relations.RARITY.NORMAL)
        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666, rarity=artifacts_relations.RARITY.NORMAL)
        self.assertTrue(self.hero.bag._compare_drop(distribution, artifact, loot))

    def test_compare_drop__useless_and_artifact(self):
        distribution = self.hero.preferences.archetype.power_distribution

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=artifacts_relations.RARITY.NORMAL)
        loot = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 666, rarity=artifacts_relations.RARITY.NORMAL)
        self.assertFalse(self.hero.bag._compare_drop(distribution, loot, artifact))

    def test_compare_drop__artifact_and_artifact(self):
        artifact_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=artifacts_relations.RARITY.NORMAL)
        artifact_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=artifacts_relations.RARITY.NORMAL)

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
        artifact_1 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact_2 = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)

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

    def test_repair_artifact(self):
        for artifact in self.hero.equipment.values():
            artifact.integrity = 0

        artifact = self.hero.repair_artifact()

        self.assertEqual(artifact.integrity, artifact.max_integrity)
        self.assertEqual(self.hero.equipment.get(artifact.type.equipment_slot), artifact)


    def test_repair_artifact__only_damaged_artifacts(self):

        test_artifact = random.choice(self.hero.equipment.values())

        for i in xrange(100):

            for artifact in self.hero.equipment.values():
                artifact.integrity = 0

            test_artifact.integrity = test_artifact.max_integrity

            artifact = self.hero.repair_artifact()

            self.assertEqual(artifact.integrity, artifact.max_integrity)
            self.assertNotEqual(artifact, test_artifact)

            self.assertEqual(test_artifact.integrity, test_artifact.max_integrity)

    def test_repair_artifact__single_damaged_artifact(self):

        test_artifact = random.choice(self.hero.equipment.values())

        for i in xrange(100):

            for artifact in self.hero.equipment.values():
                artifact.integrity = artifact.max_integrity

            test_artifact.integrity = 0

            artifact = self.hero.repair_artifact()

            self.assertEqual(artifact.integrity, artifact.max_integrity)
            self.assertEqual(artifact, test_artifact)

    def test_sell_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(self.hero.money, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        price = self.hero.sell_artifact(artifact)

        self.assertTrue(price > 0)

        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(self.hero.money, price)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, price)

    @mock.patch('the_tale.game.heroes.objects.Hero.sell_price', lambda hero: -100)
    def test_sell_artifact__sell_price_less_than_zero(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(self.hero.money, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        self.assertEqual(self.hero.sell_artifact(artifact), 1)

        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(self.hero.money, 1)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 1)

    def test_sell_artifact__useless(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(self.hero.money, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        price = self.hero.sell_artifact(artifact)

        self.assertTrue(price > 0)

        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(self.hero.money, price)
        self.assertEqual(self.hero.statistics.money_earned_from_loot, price)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

    def test_artifacts_to_break__all_unbreakable(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
            self.hero.equipment.equip(slot, artifact)
            self.assertFalse(artifact.can_be_broken())

        self.assertEqual(self.hero.artifacts_to_break(), [])

    def test_artifacts_to_break__all_breakable(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
            artifact.integrity = slot.value
            artifact.max_integrity = 100

            self.hero.equipment.equip(slot, artifact)
            self.assertTrue(artifact.can_be_broken())

        for i in xrange(100):
            for candidate in self.hero.artifacts_to_break():
                self.assertTrue(candidate.integrity <= int(c.EQUIP_SLOTS_NUMBER * c.EQUIPMENT_BREAK_FRACTION) + 1)

    def test_artifacts_to_break__all_broken__from_all(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
            artifact.integrity = slot.value
            artifact.max_integrity = 100

            self.hero.equipment.equip(slot, artifact)
            self.assertTrue(artifact.can_be_broken())

        for i in xrange(100):
            for candidate in self.hero.artifacts_to_break(from_all=True):
                self.assertTrue(candidate.integrity <= int(c.EQUIP_SLOTS_NUMBER * c.EQUIPMENT_BREAK_FRACTION) + 1)


    @mock.patch('the_tale.game.heroes.objects.Hero.can_safe_artifact_integrity', lambda self: False)
    def test_damage_integrity(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
            self.assertEqual(artifact.integrity, artifact.max_integrity)

        self.hero.damage_integrity()

        for artifact in self.hero.equipment.values():
            self.assertTrue(artifact.integrity < artifact.max_integrity)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_safe_artifact_integrity', lambda self: True)
    def test_damage_integrity__safe(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
            self.assertEqual(artifact.integrity, artifact.max_integrity)

        self.hero.damage_integrity()

        for artifact in self.hero.equipment.values():
            self.assertEqual(artifact.integrity, artifact.max_integrity)


class ReceiveArtifactsChoicesTests(_HeroEquipmentTestsBase):

    def setUp(self):
        super(ReceiveArtifactsChoicesTests, self).setUp()

        self.assertTrue(any(artifact.power_type.is_NEUTRAL for artifact in artifacts_storage.artifacts))

        self.hero.level = 100

        self.base_artifacts = list(artifacts_storage.artifacts)

        self.artifact_most_magic = ArtifactRecordPrototype.create_random('most_magic', power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL, level=1, type_=artifacts_relations.ARTIFACT_TYPE.PLATE)
        self.artifact_magic = ArtifactRecordPrototype.create_random('magic', power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL, level=2, type_=artifacts_relations.ARTIFACT_TYPE.HELMET)
        self.artifact_neutral = ArtifactRecordPrototype.create_random('neutral', power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL, level=3, type_=artifacts_relations.ARTIFACT_TYPE.MAIN_HAND)
        self.artifact_physic = ArtifactRecordPrototype.create_random('physic', power_type=artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL, level=4, type_=artifacts_relations.ARTIFACT_TYPE.OFF_HAND)
        self.artifact_most_physic = ArtifactRecordPrototype.create_random('most_physic', power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL, level=5, type_=artifacts_relations.ARTIFACT_TYPE.CLOAK)

    def check_artifacts_lists(self, list_1, list_2):
        self.assertEqual(set([a.id for a in list_1]),
                         set([a.id for a in list_2]))


    def test_get_allowed_artifact_types__level(self):
        self.hero.level = 3

        expected_artifact_types = self.base_artifacts + [self.artifact_most_magic, self.artifact_magic, self.artifact_neutral]

        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=relations.EQUIPMENT_SLOT.records, archetype=False),
                                   expected_artifact_types)

        self.hero.level = 7

        expected_artifact_types = self.base_artifacts + [self.artifact_most_magic, self.artifact_magic, self.artifact_neutral, self.artifact_physic, self.artifact_most_physic]

        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=relations.EQUIPMENT_SLOT.records, archetype=False),
                                   expected_artifact_types)


    def test_get_allowed_artifact_types__with_archetype_magic(self):
        self.hero.preferences.set_archetype(game_relations.ARCHETYPE.MAGICAL)
        expected_artifact_types = self.base_artifacts + [self.artifact_most_magic, self.artifact_magic, self.artifact_neutral]
        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=relations.EQUIPMENT_SLOT.records, archetype=True),
                                   expected_artifact_types)

    def test_get_allowed_artifact_types__with_archetype_neutral(self):
        self.hero.preferences.set_archetype(game_relations.ARCHETYPE.NEUTRAL)
        expected_artifact_types = self.base_artifacts + [self.artifact_magic, self.artifact_neutral, self.artifact_physic]
        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=relations.EQUIPMENT_SLOT.records, archetype=True),
                                   expected_artifact_types)

    def test_get_allowed_artifact_types__with_archetype_physic(self):
        self.hero.preferences.set_archetype(game_relations.ARCHETYPE.PHYSICAL)
        expected_artifact_types = self.base_artifacts + [self.artifact_neutral, self.artifact_physic, self.artifact_most_physic]
        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=relations.EQUIPMENT_SLOT.records, archetype=True),
                                   expected_artifact_types)

    def test_get_allowed_artifact_types__slot_excluded(self):
        # without self.artifact_most_physic to remove cloaks
        expected_artifact_types = self.base_artifacts + [self.artifact_most_magic, self.artifact_magic, self.artifact_neutral, self.artifact_physic]
        slots = list(relations.EQUIPMENT_SLOT.records)
        slots.remove(relations.EQUIPMENT_SLOT.CLOAK)

        self.check_artifacts_lists(self.hero.get_allowed_artifact_types(slots=slots, archetype=False),
                                   expected_artifact_types)

    def test_receive_artifacts_slots_choices__prefered_item__no_preference(self):
        self.hero.preferences.set_favorite_item(None)
        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=False, prefered_item=True)),
                         set(relations.EQUIPMENT_SLOT.records))

    def test_receive_artifacts_slots_choices__prefered_item__has_preference(self):
        self.hero.preferences.set_favorite_item(relations.EQUIPMENT_SLOT.HELMET)
        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=False, prefered_item=True)),
                         set(relations.EQUIPMENT_SLOT.records) - set([relations.EQUIPMENT_SLOT.HELMET]))

    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', False)
    def test_receive_artifacts_slots_choices__prefered_slot__no_probability(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.CLOAK)
        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=True, prefered_item=False)),
                         set(relations.EQUIPMENT_SLOT.records))

    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', True)
    def test_prefered_slot_conflics_with_prefered_item__can_upgrade(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.HELMET)
        self.hero.preferences.set_favorite_item(relations.EQUIPMENT_SLOT.HELMET)
        self.assertEqual(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=True, prefered_item=True), [])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', False)
    def test_prefered_slot_conflics_with_prefered_item__can_not_upgrade(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.HELMET)
        self.hero.preferences.set_favorite_item(relations.EQUIPMENT_SLOT.HELMET)
        self.assertFalse(relations.EQUIPMENT_SLOT.HELMET in self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=True, prefered_item=True))


    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', True)
    def test_receive_artifacts_slots_choices__prefered_slot__no_preference(self):
        self.hero.preferences.set_equipment_slot(None)
        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=True, prefered_item=False)),
                         set(relations.EQUIPMENT_SLOT.records))

    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', True)
    def test_receive_artifacts_slots_choices__prefered_slot__has_preference(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.CLOAK)
        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=True, prefered_item=False)),
                         set([relations.EQUIPMENT_SLOT.CLOAK]))

    def test_receive_artifacts_slots_choices__better_false(self):
        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level) # pylint: disable=W0612

        for artifact in self.hero.equipment.values():
            artifact.power = max_power

        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=False, prefered_slot=False, prefered_item=False)),
                         set(relations.EQUIPMENT_SLOT.records))

    def test_receive_artifacts_slots_choices__better_true(self):
        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level) # pylint: disable=W0612

        excluded_slots = []

        for artifact in self.hero.equipment.values():
            artifact.power = max_power
            excluded_slots.append(artifact.type.equipment_slot)

        self.assertEqual(set(self.hero.receive_artifacts_slots_choices(better=True, prefered_slot=False, prefered_item=False)),
                         set(relations.EQUIPMENT_SLOT.records) - set(excluded_slots))

    @mock.patch('the_tale.game.heroes.objects.Hero.get_allowed_artifact_types', lambda self, **kwargs: ['working'])
    def test_receive_artifacts_choices__has_choices(self):
        with mock.patch('the_tale.game.heroes.objects.Hero._receive_artifacts_choices') as receive_artifacts_choices:
            self.assertEqual(self.hero.receive_artifacts_choices(better=True, prefered_slot=True, prefered_item=True, archetype=True),
                             ['working'])
        self.assertEqual(receive_artifacts_choices.call_count, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.get_allowed_artifact_types', lambda self, **kwargs: [])
    def test_receive_artifacts_choices__no_choices(self):
        with mock.patch('the_tale.game.heroes.objects.Hero._receive_artifacts_choices') as receive_artifacts_choices:
            self.hero.receive_artifacts_choices(better=True, prefered_slot=True, prefered_item=True, archetype=True)
        self.assertEqual(receive_artifacts_choices.call_args_list,
                         [mock.call(better=True, prefered_slot=False, prefered_item=True, archetype=True)])

        with mock.patch('the_tale.game.heroes.objects.Hero._receive_artifacts_choices') as receive_artifacts_choices:
            self.hero.receive_artifacts_choices(better=True, prefered_slot=False, prefered_item=True, archetype=True)
        self.assertEqual(receive_artifacts_choices.call_args_list,
                         [mock.call(better=True, prefered_slot=False, prefered_item=True, archetype=False)])

        with mock.patch('the_tale.game.heroes.objects.Hero._receive_artifacts_choices') as receive_artifacts_choices:
            self.hero.receive_artifacts_choices(better=True, prefered_slot=False, prefered_item=True, archetype=False)
        self.assertEqual(receive_artifacts_choices.call_args_list,
                         [mock.call(better=False, prefered_slot=False, prefered_item=True, archetype=False)])

        with mock.patch('the_tale.game.heroes.objects.Hero._receive_artifacts_choices') as receive_artifacts_choices:
            self.assertEqual(self.hero.receive_artifacts_choices(better=False, prefered_slot=False, prefered_item=True, archetype=False),
                             [])
        self.assertEqual(receive_artifacts_choices.call_count, 0)



class ReceiveArtifactsTests(_HeroEquipmentTestsBase):

    def setUp(self):
        super(ReceiveArtifactsTests, self).setUp()


    def test_not_equip(self):
        self.hero.equipment.serialize()
        old_equipment_data = self.hero.equipment.serialize()

        self.hero.bag.serialize()
        old_bag_data = self.hero.bag.serialize()

        self.hero.receive_artifact(equip=False, better=True, prefered_slot=True, prefered_item=True, archetype=True)

        self.hero.equipment.serialize()
        self.assertEqual(old_equipment_data, self.hero.equipment.serialize())

        self.hero.bag.serialize()
        self.assertNotEqual(old_bag_data, self.hero.bag.serialize())


    @mock.patch('the_tale.game.heroes.objects.Hero.can_upgrade_prefered_slot', True)
    def test_only_better_for_prefered_slot(self):
        self.hero.level = 9999
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.PLATE)

        # just set any artifact
        self.hero.receive_artifact(equip=True, better=False, prefered_slot=True, prefered_item=True, archetype=True)

        distribution = self.hero.preferences.archetype.power_distribution
        min_power, max_power = Power.artifact_power_interval(distribution, self.hero.level)

        for i in xrange(100):
            old_artifact = self.hero.equipment.get(relations.EQUIPMENT_SLOT.PLATE)
            old_artifact.power = max_power - Power(1, 1)

            self.hero.receive_artifact(equip=True, better=True, prefered_slot=True, prefered_item=True, archetype=True)
            self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.PLATE).preference_rating(distribution) > old_artifact.preference_rating(distribution))

    def test_base_not_equip(self):

        with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
            equipped, unequipped, coins = self.hero.receive_artifact(equip=False, better=False, prefered_slot=True, prefered_item=True, archetype=True)

        self.assertTrue(equipped in self.hero.bag.values())
        self.assertEqual(unequipped, None)
        self.assertEqual(coins, None)


    def test_base_equip__in_empty_slot(self):
        self.hero.equipment._remove_all()

        with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
            equipped, unequipped, coins = self.hero.receive_artifact(equip=True, better=False, prefered_slot=True, prefered_item=True, archetype=True)

        self.assertEqual(self.hero.equipment.get(equipped.type.equipment_slot), equipped)
        self.assertFalse(equipped in self.hero.bag.values())
        self.assertFalse(unequipped in self.hero.bag.values())
        self.assertEqual(coins, None)


    def test_base_equip__in_filled_slot(self):
        self.hero.equipment._remove_all()
        for slot in relations.EQUIPMENT_SLOT.records:
            self.hero.equipment.equip(slot, artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL))

        with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
            equipped, unequipped, coins = self.hero.receive_artifact(equip=True, better=False, prefered_slot=True, prefered_item=True, archetype=True)

        self.assertEqual(self.hero.equipment.get(equipped.type.equipment_slot), equipped)
        self.assertFalse(equipped in self.hero.bag.values())
        self.assertFalse(unequipped in self.hero.bag.values())

        self.assertTrue(coins > 0)

    def test_increment_artifact_rarity(self):

        rarity = random.choice(artifacts_relations.RARITY.records[:-1])

        for artifact in self.hero.equipment.values():
            artifact.rarity = rarity

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.increment_equipment_rarity(random.choice(self.hero.equipment.values()))

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(len([artifact for artifact in self.hero.equipment.values() if artifact.rarity == rarity]), len(self.hero.equipment.values()) - 1)
        self.assertEqual(len([artifact for artifact in self.hero.equipment.values() if artifact.rarity == artifacts_relations.RARITY(rarity.value+1)]), 1)
