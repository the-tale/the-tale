# coding: utf-8
import random
import itertools

from the_tale.common.utils.logic import random_value_by_priority
from the_tale.common.utils.storage import create_storage_class

from the_tale.game.balance import formulas as f, constants as c

from the_tale.game.artifacts.exceptions import ArtifactsException
from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.relations import ARTIFACT_TYPE


class ArtifactsStorage(create_storage_class('artifacts records change time', ArtifactRecordPrototype, ArtifactsException)):

    def _reset_cache(self):
        self._artifacts_by_uuids = {}
        self.artifacts = []
        self.loot = []
        self._artifacts_by_types = { artifact_type: [] for artifact_type in ARTIFACT_TYPE._records}
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

        if not item.state.is_enabled:
            return

        if item.type._is_USELESS:
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
            if artifact_record.state.is_enabled and artifact_record.accepted_for_level(level):
                artifact_choices.append((artifact_record, artifact_record.priority))

        artifact_record = random_value_by_priority(artifact_choices)

        if artifact_record is None:
            return None

        if artifact_record.is_useless:
            power = 0
        else:
            power = f.power_to_artifact_randomized(level)

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


    def generate_loot(self, mob):

        if random.uniform(0, 1) < f.artifacts_per_battle(mob.level):
            return self.generate_artifact_from_list(self.get_mob_artifacts(mob.record.id), mob.level)

        if random.uniform(0, 1) < c.GET_LOOT_PROBABILITY:
            return self.generate_artifact_from_list(self.get_mob_loot(mob.record.id), mob.record.level)

        return None



artifacts_storage = ArtifactsStorage()
