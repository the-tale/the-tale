# coding: utf-8
import random
import itertools

from the_tale.common.utils import storage
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.balance.power import Power

from the_tale.game.artifacts import exceptions
from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts import relations


class ArtifactsStorage(storage.CachedStorage):
    SETTINGS_KEY = 'artifacts records change time'
    EXCEPTION = exceptions.ArtifactsStorageError
    PROTOTYPE = ArtifactRecordPrototype

    def _reset_cache(self):
        self._artifacts_by_uuids = {}
        self.artifacts = []
        self.loot = []
        self._artifacts_by_types = { artifact_type: [] for artifact_type in relations.ARTIFACT_TYPE.records}
        self._mob_artifacts = {}
        self._mob_loot = {}

    def _update_cached_data(self, item):
        self._artifacts_by_uuids[item.uuid] = item

        if not item.state.is_ENABLED:
            return

        if item.type.is_USELESS:
            self.loot.append(item)
        else:
            self.artifacts.append(item)

        self._artifacts_by_types[item.type].append(item)

        self._mob_artifacts = {}
        self._mob_loot = {}

    def get_by_uuid(self, uuid):
        self.sync()
        return self._artifacts_by_uuids[uuid]

    def has_artifact(self, uuid):
        self.sync()
        return uuid in self._artifacts_by_uuids

    def artifacts_for_type(self, types):
        return list(itertools.chain(*[self._artifacts_by_types[type_] for type_ in types] ))

    def generate_artifact_from_list(self, artifacts_list, level, rarity):

        artifact_choices = []

        for artifact_record in artifacts_list:
            if artifact_record.state.is_ENABLED and artifact_record.accepted_for_level(level):
                artifact_choices.append(artifact_record)

        if not artifact_choices:
            return None

        artifact_record = random.choice(artifact_choices)

        if artifact_record.is_useless:
            power = Power(0, 0)
        else:
            power = Power.artifact_power_randomized(distribution=artifact_record.power_type.distribution,
                                                    level=level)

        return artifact_record.create_artifact(level=level,
                                               power=power,
                                               rarity=rarity)


    def get_mob_artifacts(self, mob_id):
        self.sync()

        if mob_id not in self._mob_artifacts:
            self._mob_artifacts[mob_id] = filter(lambda artifact: artifact.mob_id == mob_id, self.artifacts) # pylint: disable=W0110
        return self._mob_artifacts[mob_id]

    def get_mob_loot(self, mob_id):
        self.sync()

        if mob_id not in self._mob_loot:
            self._mob_loot[mob_id] = filter(lambda artifact: artifact.mob_id == mob_id, self.loot) # pylint: disable=W0110
        return self._mob_loot[mob_id]

    def get_rarity_type(self, hero):
        choices = ( (relations.RARITY.NORMAL, relations.RARITY.NORMAL.probability),
                    (relations.RARITY.RARE, relations.RARITY.RARE.probability * hero.rare_artifact_probability_multiplier),
                    (relations.RARITY.EPIC, relations.RARITY.EPIC.probability * hero.epic_artifact_probability_multiplier))
        return random_value_by_priority(choices)

    def generate_loot(self, hero, mob):

        if random.uniform(0, 1) < hero.artifacts_probability(mob):
            return self.generate_artifact_from_list(self.get_mob_artifacts(mob.record.id), mob.level, rarity=self.get_rarity_type(hero))

        if random.uniform(0, 1) < hero.loot_probability(mob):
            return self.generate_artifact_from_list(self.get_mob_loot(mob.record.id), mob.record.level, rarity=relations.RARITY.NORMAL)

        return None

    def generate_any_artifact(self, hero, artifact_probability_multiplier=1.0):

        artifact_level = random.randint(1, hero.level)

        if random.uniform(0, 1) < hero.artifacts_probability(None) * artifact_probability_multiplier:
            return self.generate_artifact_from_list(self.artifacts, artifact_level, rarity=self.get_rarity_type(hero))

        return self.generate_artifact_from_list(self.loot, artifact_level, rarity=relations.RARITY.NORMAL)



artifacts_storage = ArtifactsStorage()
