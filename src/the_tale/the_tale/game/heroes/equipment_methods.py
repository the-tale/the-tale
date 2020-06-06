
import smart_imports

smart_imports.all()


class EquipmentMethodsMixin(object):
    __slots__ = ()

    @property
    def bag_is_full(self):
        return self.bag.occupation >= self.max_bag_size

    def put_loot(self, artifact, force=False):
        if self.bag_is_full and not force:
            return None

        if artifact.is_useless:
            self.statistics.change_loot_had(1)
        else:
            self.statistics.change_artifacts_had(1)

        if not artifact.type.is_USELESS:
            artifact.power += self.bonus_artifact_power

        self.bag.put_artifact(artifact)

        return artifact.bag_uuid

    def pop_loot(self, artifact):
        self.bag.pop_artifact(artifact)

    def get_allowed_artifact_types(self, slots, archetype):
        return [artifact
                for artifact in artifacts_storage.artifacts.artifacts_for_type(types=[slot.artifact_type for slot in slots])
                if ((artifact.level <= self.level) and
                    (not archetype or (artifact.power_type in self.preferences.archetype.allowed_power_types)))]

    def receive_artifacts_slots_choices(self, better, prefered_slot, prefered_item):
        allowed_slots = list(relations.EQUIPMENT_SLOT.records)
        slot_choices = list(allowed_slots)

        if prefered_slot and self.preferences.equipment_slot and self.can_upgrade_prefered_slot:
            slot_choices = [self.preferences.equipment_slot]

        if prefered_item and self.preferences.favorite_item and self.preferences.favorite_item in slot_choices:  # after prefered slot, since prefered item is more important
            slot_choices.remove(self.preferences.favorite_item)

        result_choices = []

        if better:

            for slot in slot_choices:
                artifact = self.equipment.get(slot)

                if artifact is not None:

                    distribution = self.preferences.archetype.power_distribution
                    min_power, max_power = power.Power.artifact_power_interval(distribution, self.level)  # pylint: disable=W0612

                    if artifact.preference_rating(distribution) >= artifacts_objects.Artifact._preference_rating(artifact.rarity, max_power, distribution):
                        continue

                result_choices.append(slot)

        else:
            result_choices = slot_choices

        return result_choices

    def _receive_artifacts_choices(self, **kwargs):
        return self.receive_artifacts_choices(**kwargs)

    def receive_artifacts_choices(self, better, prefered_slot, prefered_item, archetype):
        slot_choices = self.receive_artifacts_slots_choices(better=better,
                                                            prefered_slot=prefered_slot,
                                                            prefered_item=prefered_item)

        artifacts_choices = self.get_allowed_artifact_types(slots=slot_choices, archetype=archetype)

        if not artifacts_choices:

            # remove restrictions
            if prefered_slot:
                prefered_slot = False
            # флаг archetype обнуляется перед better, так как на better завязаны некоторые обязательные эффекты, например, у карт судьбы
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

    def receive_artifact(self, equip, better, prefered_slot, prefered_item, archetype, rarity_type=None, level_delta=0):

        artifact_choices = self.receive_artifacts_choices(better=better,
                                                          prefered_slot=prefered_slot,
                                                          prefered_item=prefered_item,
                                                          archetype=archetype)

        if rarity_type is None:
            rarity_type = artifacts_storage.artifacts.get_rarity_type(self)

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifact_choices, max(1, self.level + level_delta), rarity_type)

        if artifact is None:
            return None, None, None

        self.put_loot(artifact, force=True)

        slot = artifact.type.equipment_slot
        unequipped = self.equipment.get(slot)

        distribution = self.preferences.archetype.power_distribution

        if (better and unequipped is not None and
                artifact.preference_rating(distribution) <= unequipped.preference_rating(distribution)):
            artifact.make_better_than(unequipped, distribution)

        if not equip:
            return artifact, None, None

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

        min_power, max_power = power.Power.artifact_power_interval(distribution, self.level)  # pylint: disable=W0612

        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None and artifact.sharp(distribution, max_power):
                self.equipment.mark_updated()
                return artifact

        # if all artifacts are on maximum level
        random.shuffle(choices)
        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None and artifact.sharp(distribution, max_power, force=True):
                self.equipment.mark_updated()
                return artifact

    def damage_integrity(self):
        if random.random() < self.safe_artifact_integrity_probability:
            return

        expected_artifact_power = power.Power.normal_power_to_level(self.level)

        for artifact in self.equipment.values():
            delta = c.ARTIFACT_INTEGRITY_DAMAGE_PER_BATTLE * (float(artifact.power.total()) / expected_artifact_power)**2

            if self.preferences.favorite_item is not None and self.preferences.favorite_item == artifact.type.equipment_slot:
                delta *= c.ARTIFACT_INTEGRITY_DAMAGE_FOR_FAVORITE_ITEM

            artifact.damage_integrity(delta)

    def artifacts_to_break(self, from_all=False):
        if from_all:
            artifacts = list(self.equipment.values())
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

        slot = utils_logic.random_value_by_priority(choices)

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

        self.force_save_required = True

        if unequipped:
            self.equipment.unequip(slot)
            self.bag.put_artifact(unequipped)

        if equipped:
            self.bag.pop_artifact(equipped)
            self.equipment.equip(slot, equipped)

        self.reset_accessors_cache()

    def increment_equipment_rarity(self, artifact):
        artifact.rarity = artifacts_relations.RARITY(artifact.rarity.value + 1)
        artifact.power = power.Power.artifact_power_randomized(distribution=artifact.record.power_type.distribution,
                                                               level=self.level)
        artifact.max_integrity = int(artifact.rarity.max_integrity * random.uniform(1 - c.ARTIFACT_MAX_INTEGRITY_DELTA, 1 + c.ARTIFACT_MAX_INTEGRITY_DELTA))
        self.reset_accessors_cache()

    def randomize_equip(self):
        for slot in relations.EQUIPMENT_SLOT.records:
            self.equipment.unequip(slot)

            artifacts_list = self.receive_artifacts_choices(better=False,
                                                            prefered_slot=False,
                                                            prefered_item=False,
                                                            archetype=True)

            artifacts_list = [artifact for artifact in artifacts_list if artifact.type.equipment_slot == slot]

            if not artifacts_list:
                continue

            artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_list, self.level, rarity=artifacts_relations.RARITY.NORMAL)

            self.equipment.equip(slot, artifact)

    def compare_artifacts(self, a, b):
        if a.type.is_USELESS:
            if b.type.is_USELESS:
                return a.absolute_sell_price() > b.absolute_sell_price()
            else:
                return False

        else:
            if b.type.is_USELESS:
                return True
            else:
                distribution = self.preferences.archetype.power_distribution

                return a.preference_rating(distribution) > b.preference_rating(distribution)

    def get_worst_item_in_bag(self):
        worst_item = None

        for item in self.bag.values():
            if worst_item is None:
                worst_item = item
                continue

            if self.compare_artifacts(worst_item, item):
                worst_item = item

        return worst_item
