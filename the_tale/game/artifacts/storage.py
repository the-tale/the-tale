# coding: utf-8
import random
import itertools

from common.utils.logic import random_value_by_priority
from common.utils.storage import create_storage_class

from game.balance import formulas as f, constants as c

from game.artifacts.exceptions import ArtifactsException
from game.artifacts.prototypes import ArtifactRecordPrototype
from game.artifacts.models import ArtifactRecord, ARTIFACT_TYPE


class ArtifactsStorage(create_storage_class('artifacts records change time', ArtifactRecord, ArtifactRecordPrototype, ArtifactsException)):

    def refresh(self):
        super(ArtifactsStorage, self).refresh()
        self._artifacts_by_uuids = dict( (mob.uuid, mob) for mob in self.all())

        self.artifacts = filter(lambda artifact_record: artifact_record.state.is_enabled and not artifact_record.type.is_useless, self.all())
        self.loot = filter(lambda artifact_record: artifact_record.state.is_enabled and artifact_record.type.is_useless, self.all())

        self._artifacts_by_types = {}
        for artifact_type in ARTIFACT_TYPE._ALL:
            self._artifacts_by_types[artifact_type] = filter(lambda artifact_record: artifact_record.state.is_enabled and artifact_record.type == artifact_type, self.all())

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

    def generate_artifact_from_list(self, artifacts_list, level):

        artifact_choices = []

        for artifact_record in artifacts_list:
            if artifact_record.state.is_enabled and artifact_record.accepted_for_level(level):
                artifact_choices.append((artifact_record, artifact_record.priority))

        artifact_record = random_value_by_priority(artifact_choices)

        if artifact_record is None:
            return None

        if artifact_record.type.is_useless:
            power = 0
        else:
            power = f.power_to_artifact_randomized(level)

        return artifact_record.create_artifact(level=level, power=power)


    def get_mob_artifacts(self, mob_id):
        self.sync()

        if mob_id not in self._mob_artifacts:
            self._mob_artifacts[mob_id] = filter(lambda artifact: artifact.mob_id == mob_id, self.artifacts)
        return self._mob_artifacts[mob_id]

    def get_mob_loot(self, mob_id):
        self.sync()

        if mob_id not in self._mob_loot:
            self._mob_loot[mob_id] = filter(lambda artifact: artifact.mob_id == mob_id, self.loot)
        return self._mob_loot[mob_id]


    def generate_loot(self, mob):

        if random.uniform(0, 1) < f.artifacts_per_battle(mob.level):
            return self.generate_artifact_from_list(self.get_mob_artifacts(mob.record.id), mob.level)

        if random.uniform(0, 1) < c.GET_LOOT_PROBABILITY:
            return self.generate_artifact_from_list(self.get_mob_loot(mob.record.id), mob.record.level)

        return None



artifacts_storage = ArtifactsStorage()
