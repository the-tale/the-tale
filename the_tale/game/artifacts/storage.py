# coding: utf-8
import random
import numbers

import xlrd

from common.utils.logic import random_value_by_priority

from collections import namedtuple

from game.balance import formulas as f, constants as c

from game.artifacts.conf import artifacts_settings, ITEM_TYPE, ITEM_TYPE_STR_2_ID, EQUIP_TYPE_STR_2_ID, RARITY_TYPE_STR_2_ID, RARITY_TYPE_2_PRIORITY
from game.artifacts.exceptions import ArtifactsException
from game.artifacts.prototypes import ArtifactPrototype


class ArtifactRecord(namedtuple('ArtifactRecord', ('id', 'type', 'slot', 'name', 'normalized_name', 'morph', 'min_lvl', 'max_lvl', 'rarity'))):
    __slots__ = ()

    @property
    def is_useless(self): return self.type == ITEM_TYPE.USELESS

    @property
    def priority(self): return RARITY_TYPE_2_PRIORITY[self.rarity]

    def accepted_for_level(self, level): return self.min_lvl <= level <= self.max_lvl


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

            artifact_data[-4] = tuple([morph for morph in artifact_data[-4].split(',') if morph])

            artifact_data[-3] = int(artifact_data[-3]) if isinstance(artifact_data[-3], numbers.Number) else 0
            artifact_data[-2] = int(artifact_data[-2]) if isinstance(artifact_data[-2], numbers.Number) else artifacts_settings.INFINITY_ARTIFACT_LEVEL
            artifact_data[-1] = RARITY_TYPE_STR_2_ID[artifact_data[-1]]

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

    def create_artifact(self, id_, level, power=0, quest=False):
        return ArtifactPrototype(record=self.data[id_],
                                 power=power,
                                 quest=quest,
                                 level=level)

    def generate_artifact_from_list(self, artifacts_list, level):

        artifact_choices = []

        for artifact_id in artifacts_list:
            artifact_record = self.data[artifact_id]
            if artifact_record.accepted_for_level(level):
                artifact_choices.append((artifact_record, artifact_record.priority))

        artifact_record = random_value_by_priority(artifact_choices)

        if artifact_record.type == ITEM_TYPE.USELESS:
            power = 0
        else:
            power = f.power_to_artifact_randomized(level)

        return self.create_artifact(artifact_record.id, level=level, power=power)


    def generate_loot(self, artifacts_list, loot_list, artifact_level, loot_level):

        if random.uniform(0, 1) < f.artifacts_per_battle(artifact_level):
            return self.generate_artifact_from_list(artifacts_list, artifact_level)

        if random.uniform(0, 1) < c.GET_LOOT_PROBABILITY:
            return self.generate_artifact_from_list(loot_list, loot_level)

        return None
