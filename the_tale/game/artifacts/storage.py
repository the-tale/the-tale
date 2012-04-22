# coding: utf-8
import random

import xlrd

from collections import namedtuple

from game.balance import formulas as f, constants as c

from game.artifacts.conf import artifacts_settings, ITEM_TYPE, ITEM_TYPE_STR_2_ID, EQUIP_TYPE_STR_2_ID
from game.artifacts.exceptions import ArtifactsException
from game.artifacts.prototypes import ArtifactPrototype


ArtifactRecord = namedtuple('ArtifactRecord', ('id', 'type', 'slot', 'name', 'normalized_name', 'min_lvl', 'max_lvl'))

class ArtifactsDatabase(object):

    def __init__(self):
        self.data = {}

    @property
    def artifacts_ids(self):
        return [artifact_id for artifact_id, artifact_record in self.data.items() if artifact_record.type != ITEM_TYPE.USELESS]

    @property
    def loot_ids(self):
        return [artifact_id for artifact_id, artifact_record in self.data.items() if artifact_record.type == ITEM_TYPE.USELESS]

    def get_artifact_record(self, id_):  return self.data[id_]

    def load(self, filename):

        book = xlrd.open_workbook(filename, logfile=None, encoding_override='utf-8')

        sheet = book.sheet_by_index(0)

        for row_number in xrange(sheet.nrows):
            artifact_data = list(sheet.row_values(row_number))

            if artifact_data[0] != u'+':
                continue

            artifact_data = artifact_data[1:]

            artifact_data[1] = ITEM_TYPE_STR_2_ID[artifact_data[1]]
            artifact_data[2] = EQUIP_TYPE_STR_2_ID[artifact_data[2]]
            artifact_data[-1] = int(artifact_data[-1]) if artifact_data[-1] else 0
            artifact_data[-2] = int(artifact_data[-2]) if artifact_data[-2] else 0
            artifact_record = ArtifactRecord(*artifact_data)

            if artifact_record.id in self.data:
                raise ArtifactsException(u'duplicate artifact id: %s' % artifact_record.id)

            self.data[artifact_record.id] = artifact_record


    @classmethod
    def storage(cls):
        if not hasattr(cls, '_storage'):
            cls._storage = cls()
            cls._storage.load(artifacts_settings.ARTIFACTS_STORAGE)
            cls._storage.load(artifacts_settings.LOOT_STORAGE)
        return cls._storage

    def create_artifact(self, id_, power=0, quest=False):
        return ArtifactPrototype(record=self.data[id_],
                                 power=power,
                                 quest=quest)

    def generate_artifact_from_list(self, artifacts_list, level):

        artifacts = []
        for artifact_id in artifacts_list:
            artifact_record = self.data[artifact_id]
            if artifact_record.type == ITEM_TYPE.USELESS or (artifact_record.min_lvl <= level <= artifact_record.max_lvl):
                artifacts.append(artifact_record)

        artifact_record = random.choice(artifacts)

        if artifact_record.type == ITEM_TYPE.USELESS:
            power = 0
        else:
            power = f.power_to_artifact_randomized(level)

        return self.create_artifact(artifact_id, power=power)


    def generate_loot(self, artifacts_list, loot_list, level):

        if random.uniform(0, 1) < f.artifacts_per_battle(level):
            return self.generate_artifact_from_list(artifacts_list, level)

        if random.uniform(0, 1) < c.GET_LOOT_PROBABILITY:
            return self.generate_artifact_from_list(loot_list, level)

        return None
