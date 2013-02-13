# coding: utf-8
import random

from common.utils.logic import random_value_by_priority
from common.utils.storage import create_storage_class

from game.balance import formulas as f, constants as c

from game.artifacts.exceptions import ArtifactsException
from game.artifacts.prototypes import ArtifactPrototype, ArtifactRecordPrototype
from game.artifacts.models import ArtifactRecord


class ArtifactsStorage(create_storage_class('artifacts records change time', ArtifactRecord, ArtifactRecordPrototype, ArtifactsException)):

    def refresh(self):
        super(ArtifactsStorage, self).refresh()
        self._artifacts_by_uuids = dict( (mob.uuid, mob) for mob in self.all())

    def get_by_uuid(self, uuid):
        self.sync()
        return self._artifacts_by_uuids[uuid]

    def has_artifact(self, uuid):
        self.sync()
        return uuid in self._artifacts_by_uuids

    @property
    def artifacts_ids(self):
        return [artifact_record.uuid for artifact_record in self.all() if artifact_record.state.is_enabled and not artifact_record.type.is_useless]

    @property
    def loot_ids(self):
        return [artifact_record.uuid for artifact_record in self.all() if artifact_record.state.is_enabled and artifact_record.type.is_useless]

    # artifacts_for_equip_type
    def artifacts_for_type(self, types):
        return [artifact_record.uuid for artifact_record in self.all() if artifact_record.state.is_enabled and artifact_record.type in types]

    def create_artifact(self, uuid, level, power=0, quest=False):
        return ArtifactPrototype(record=self.get_by_uuid(uuid),
                                 power=power,
                                 quest=quest,
                                 level=level)

    def generate_artifact_from_list(self, artifacts_list, level):

        artifact_choices = []

        for artifact_uuid in artifacts_list:
            artifact_record = self.get_by_uuid(artifact_uuid)
            if artifact_record.state.is_enabled and artifact_record.accepted_for_level(level):
                artifact_choices.append((artifact_record, artifact_record.priority))

        artifact_record = random_value_by_priority(artifact_choices)

        if artifact_record is None:
            return None

        if artifact_record.type.is_useless:
            power = 0
        else:
            power = f.power_to_artifact_randomized(level)

        return self.create_artifact(artifact_record.uuid, level=level, power=power)


    def generate_loot(self, artifacts_list, loot_list, artifact_level, loot_level):

        if random.uniform(0, 1) < f.artifacts_per_battle(artifact_level):
            return self.generate_artifact_from_list(artifacts_list, artifact_level)

        if random.uniform(0, 1) < c.GET_LOOT_PROBABILITY:
            return self.generate_artifact_from_list(loot_list, loot_level)

        return None



artifacts_storage = ArtifactsStorage()
