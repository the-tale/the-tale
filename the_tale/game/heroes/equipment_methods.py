# coding: utf-8

import random

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.balance.power import Power
from the_tale.game.balance import constants as c

from the_tale.game.heroes import relations

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts import relations as artifacts_relations


class EquipmentMethodsMixin(object):
    __slots__ = ()

    def put_loot(self, artifact, force=False):
        if force or not self.bag_is_full:
            if not artifact.type.is_USELESS:
                artifact.power += self.bonus_artifact_power
            self.bag.put_artifact(artifact)
            return artifact.bag_uuid

    def pop_loot(self, artifact):
        self.bag.pop_artifact(artifact)


    def get_allowed_artifact_types(self, slots, archetype):
        return [artifact
                for artifact in artifacts_storage.artifacts_for_type(types=[slot.artifact_type for slot in slots])
                if ((artifact.level <= self.level) and
                    ( not archetype or (artifact.power_type in self.preferences.archetype.allowed_power_types)))]

    def receive_artifacts_slots_choices(self, better, prefered_slot, prefered_item):
        from the_tale.game.artifacts.prototypes import ArtifactPrototype

        allowed_slots = list(relations.EQUIPMENT_SLOT.records)
        slot_choices = list(allowed_slots)

        if prefered_slot and self.preferences.equipment_slot and self.can_upgrade_prefered_slot:
            slot_choices = [self.preferences.equipment_slot]

        if prefered_item and self.preferences.favorite_item and self.preferences.favorite_item in slot_choices: #after prefered slot, since prefered item is more important
            slot_choices.remove(self.preferences.favorite_item)

        result_choices = []

        if better:

            for slot in slot_choices:
                artifact = self.equipment.get(slot)

                if artifact is not None:

                    distribution = self.preferences.archetype.power_distribution
                    min_power, max_power = Power.artifact_power_interval(distribution, self.level) # pylint: disable=W0612

                    if artifact.preference_rating(distribution) >= ArtifactPrototype._preference_rating(artifact.rarity, max_power, distribution):
                        continue

                result_choices.append(slot)

        else:
            result_choices = slot_choices

        return result_choices


    def _receive_artifacts_choices(self, **kwargs):
        return self.receive_artifacts_choices(**kwargs)

    def receive_artifacts_choices(self, better, prefered_slot, prefered_item, archetype):
        slot_choices = self.receive_artifacts_slots_choices(better=better, prefered_slot=prefered_slot, prefered_item=prefered_item)

        artifacts_choices = self.get_allowed_artifact_types(slots=slot_choices, archetype=archetype)

        if not artifacts_choices:

            # remove restrictions
            if prefered_slot:
                prefered_slot = False
            elif archetype:
                archetype = False
            elif better:
                better = False
            else:
                return []

            return self._receive_artifacts_choices(better=better,
                                                   prefered_slot=prefered_slot,
                                                   prefered_item=prefered_item,
                                                   archetype=archetype)

        return artifacts_choices

    def receive_artifact(self, equip, better, prefered_slot, prefered_item, archetype, rarity_type=None, power_bonus=0, level_delta=0):

        artifact_choices = self.receive_artifacts_choices(better=better, prefered_slot=prefered_slot, prefered_item=prefered_item, archetype=archetype)

        if rarity_type is None:
            rarity_type = artifacts_storage.get_rarity_type(self)

        artifact = artifacts_storage.generate_artifact_from_list(artifact_choices, max(1, self.level + level_delta), rarity_type)

        artifact.power += Power(int(artifact.power.physic * power_bonus),
                                int(artifact.power.magic * power_bonus))

        if artifact is None:
            return None, None, None

        self.bag.put_artifact(artifact)
        self.statistics.change_artifacts_had(1)

        if not equip:
            return artifact, None, None

        slot = artifact.type.equipment_slot
        unequipped = self.equipment.get(slot)

        distribution = self.preferences.archetype.power_distribution

        if (better and unequipped is not None and
            artifact.preference_rating(distribution) <= unequipped.preference_rating(distribution)):
            artifact.make_better_than(unequipped, distribution)

        self.change_equipment(slot, unequipped, artifact)

        sell_price = None

        if unequipped is not None:
            sell_price = self.sell_artifact(unequipped)

        return artifact, unequipped, sell_price

    def sell_artifact(self, artifact):
        sell_price = int(max(1, artifact.get_sell_price() * self.sell_price()))

        if artifact.is_useless:
            money_source = relations.MONEY_SOURCE.EARNED_FROM_LOOT
        else:
            money_source = relations.MONEY_SOURCE.EARNED_FROM_ARTIFACTS

        self.change_money(money_source, sell_price)
        self.bag.pop_artifact(artifact)

        return sell_price

    def sharp_artifact(self):
        choices = list(relations.EQUIPMENT_SLOT.records)
        random.shuffle(choices)

        if self.preferences.equipment_slot is not None and self.can_upgrade_prefered_slot:
            choices.insert(0, self.preferences.equipment_slot)

        distribution = self.preferences.archetype.power_distribution

        min_power, max_power = Power.artifact_power_interval(distribution, self.level) # pylint: disable=W0612

        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None and artifact.sharp(distribution, max_power):
                self.equipment.updated = True
                return artifact

        # if all artifacts are on maximum level
        random.shuffle(choices)
        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None and artifact.sharp(distribution, max_power, force=True):
                self.equipment.updated = True
                return artifact

    def damage_integrity(self):
        for artifact in self.equipment.values():
            if not self.can_safe_artifact_integrity(artifact):
                artifact.damage_integrity()


    def artifacts_to_break(self, from_all=False):
        if from_all:
            artifacts = self.equipment.values()
        else:
            artifacts = [artifact
                         for artifact in self.equipment.values()
                         if artifact.can_be_broken()]
        return sorted(artifacts, key=lambda a: a.integrity_fraction)[:int(c.EQUIP_SLOTS_NUMBER * c.EQUIPMENT_BREAK_FRACTION) + 1]

    def repair_artifact(self):
        artifacts = self.artifacts_to_break()

        if not artifacts:
            artifacts = self.artifacts_to_break(from_all=True)

        if not artifacts:
            return None

        choices = []
        for artifact in artifacts:
            slot = artifact.type.equipment_slot
            if self.preferences.favorite_item == slot:
                choices.append((slot, c.SPECIAL_SLOT_REPAIR_PRIORITY))
            if self.preferences.equipment_slot == slot:
                choices.append((slot, c.SPECIAL_SLOT_REPAIR_PRIORITY))
            else:
                choices.append((slot, c.NORMAL_SLOT_REPAIR_PRIORITY))

        slot = random_value_by_priority(choices)

        artifact = self.equipment.get(slot)
        artifact.repair_it()

        return artifact


    def get_equip_candidates(self):

        distribution = self.preferences.archetype.power_distribution

        for artifact in self.bag.values():
            if not artifact.can_be_equipped:
                continue

            slot = artifact.type.equipment_slot

            if self.preferences.favorite_item == slot:
                continue

            equipped_artifact = self.equipment.get(slot)

            if equipped_artifact is None:
                return slot, None, artifact

            equipped_preference_rating = equipped_artifact.preference_rating(distribution)
            new_preference_rating = artifact.preference_rating(distribution)

            if equipped_preference_rating < new_preference_rating:
                return slot, equipped_artifact, artifact

            if equipped_preference_rating == new_preference_rating and equipped_artifact.integrity < artifact.integrity:
                return slot, equipped_artifact, artifact

        return None, None, None

    def equip_from_bag(self):
        slot, unequipped, equipped = self.get_equip_candidates()
        self.change_equipment(slot, unequipped, equipped)
        return slot, unequipped, equipped

    def change_equipment(self, slot, unequipped, equipped):
        if unequipped:
            self.equipment.unequip(slot)
            self.bag.put_artifact(unequipped)

        if equipped:
            self.bag.pop_artifact(equipped)
            self.equipment.equip(slot, equipped)

        self.reset_accessors_cache()


    def increment_equipment_rarity(self, artifact):
        artifact.rarity = artifacts_relations.RARITY(artifact.rarity.value+1)
        self.reset_accessors_cache()


    def randomize_equip(self):
        for slot in relations.EQUIPMENT_SLOT.records:
            self.equipment.unequip(slot)

            artifacts_list = self.receive_artifacts_choices(better=False, prefered_slot=False, prefered_item=False, archetype=True)

            artifacts_list = [artifact for artifact in artifacts_list if artifact.type.equipment_slot == slot]

            if not artifacts_list:
                continue

            artifact = artifacts_storage.generate_artifact_from_list(artifacts_list, self.level, rarity=artifacts_relations.RARITY.NORMAL)

            self.equipment.equip(slot, artifact)
