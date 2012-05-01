# coding: utf-8
import random

import xlrd

from collections import namedtuple

from game.mobs.conf import mobs_settings
from game.mobs.exceptions import MobsException
from game.mobs.prototypes import MobPrototype
from game.map.places.models import TERRAIN_STR_2_ID

MobRecord = namedtuple('MobRecord', ('level', 'id', 'name', 'normalized_name', 'morph', 'speed', 'health', 'damage', 'abilities', 'terrain', 'loot', 'artifacts'))


class MobsDatabase(object):

    def __init__(self):
        self.data = {}

    @staticmethod
    def _prepair_string_set(string_data):
        sequence = [data.strip() for data in string_data.split(',')]
        if sequence == [u'']:
            sequence = []
        return frozenset(sequence)

    def load(self, filename):

        book = xlrd.open_workbook(filename, logfile=None, encoding_override='utf-8')

        sheet = book.sheet_by_index(0)

        for row_number in xrange(sheet.nrows):
            mob_data = list(sheet.row_values(row_number))

            if mob_data[0] != u'+':
                continue

            mob_data = mob_data[1:]

            mob_data[0] = int(mob_data[0])

            mob_data[4] = tuple([morph for morph in mob_data[4].split(',') if morph])
            mob_data[5] = float(mob_data[5])
            mob_data[6] = float(mob_data[6])
            mob_data[7] = float(mob_data[7])

            mob_data[8] = self._prepair_string_set(mob_data[8])

            mob_data[9] = self._prepair_string_set(mob_data[9])
            mob_data[9] = frozenset([TERRAIN_STR_2_ID[terrain] for terrain in mob_data[9]])

            mob_data[10] = self._prepair_string_set(mob_data[10])
            mob_data[11] = self._prepair_string_set(mob_data[11])

            mob_record = MobRecord(*mob_data)

            if mob_record.id in self.data:
                raise MobsException(u'duplicate mob id: %s' % mob_record.id)

            self.data[mob_record.id] = mob_record


    @classmethod
    def storage(cls):
        if not hasattr(cls, '_storage'):
            cls._storage = cls()
            cls._storage.load(mobs_settings.MOBS_STORAGE)
        return cls._storage


    def get_available_mobs_list(self, level, terrain):
        mobs = []
        for mob_record in self.data.values():
            if terrain in mob_record.terrain and mob_record.level <= level:
                mobs.append(mob_record)
        return mobs


    @classmethod
    def get_random_mob(cls, hero):
        mob_record = random.choice(cls.storage().get_available_mobs_list(level=hero.level, terrain=hero.position.get_terrain()))
        return MobPrototype(record=mob_record, level=hero.level)
