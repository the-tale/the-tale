# coding: utf-8
import random
import itertools

from the_tale.common.utils.storage import create_storage_class

from the_tale.game.balance.power import Power

from the_tale.game.artifacts import exceptions
from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.relations import ARTIFACT_TYPE


class ArtifactsStorage(create_storage_class('artifacts records change time', ArtifactRecordPrototype, exceptions.ArtifactsStorageError)):

    def _reset_cache(self):
        self._artifacts_by_uuids = {}
        self.artifacts = []
        self.loot = []
        self._artifacts_by_types = { artifact_type: [] for artifact_type in ARTIFACT_TYPE.records}
        self._mob_artifacts = {}
        self._mob_loot = {}

    def refresh(self):
        self._reset_cache()
        super(ArtifactsStorage, self).refresh()

    def clear(self):
        self._reset_cache()
        super(ArtifactsStorage, self).clear()

    def update_cached_data(self, item):
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

    def add_item(self, id_, item):
        super(ArtifactsStorage, self).add_item(id_, item)
        self.update_cached_data(item)

    def get_by_uuid(self, uuid):
        self.sync()
        return self._artifacts_by_uuids[uuid]

    def has_artifact(self, uuid):
        self.sync()
        return uuid in self._artifacts_by_uuids

    def artifacts_for_type(self, types):
        return list(itertools.chain(*[self._artifacts_by_types[type_] for type_ in types] ))

    def generate_artifact_from_list(self, artifacts_list, level):

        artifact_choices = []

        for artifact_record in artifacts_list:
            if artifact_record.state.is_ENABLED and artifact_record.accepted_for_level(level):
                artifact_choices.append(artifact_record)

        if not artifact_choices:
            return None

        artifact_record = random.choice(artifact_choices)

        if artifact_record.is_useless:
            power = Power.zero()
        else:
            power = Power.artifact_power_randomized(distribution=artifact_record.power_type.distribution,
                                                    level=level)

        return artifact_record.create_artifact(level=level, power=power)


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


    def generate_loot(self, mob, artifacts_probability, loot_probability):

        if random.uniform(0, 1) < artifacts_probability:
            return self.generate_artifact_from_list(self.get_mob_artifacts(mob.record.id), mob.level)

        if random.uniform(0, 1) < loot_probability:
            return self.generate_artifact_from_list(self.get_mob_loot(mob.record.id), mob.record.level)

        return None



artifacts_storage = ArtifactsStorage()
