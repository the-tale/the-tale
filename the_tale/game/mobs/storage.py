# coding: utf-8
import random

import xlrd

from collections import namedtuple

from game.mobs.conf import mobs_settings
from game.mobs.exceptions import MobsException
from game.mobs.prototypes import MobPrototype
from game.map.places.models import TERRAIN

MobRecord = namedtuple('MobRecord', ('level', 'id', 'name', 'normalized_name', 'morph', 'abilities', 'terrain', 'loot', 'artifacts'))


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

            mob_data[5] = self._prepair_string_set(mob_data[5])

            mob_data[6] = self._prepair_string_set(mob_data[6])
            mob_data[6] = frozenset([TERRAIN._STR_TO_ID[terrain.upper()] for terrain in mob_data[6]])

            mob_data[7] = self._prepair_string_set(mob_data[7])
            mob_data[8] = self._prepair_string_set(mob_data[8])

            mob_record = MobRecord(*mob_data)

            if mob_record.id in self.data:
                raise MobsException(u'duplicate mob id: %s' % mob_record.id)

            self.data[mob_record.id] = mob_record

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    @classmethod
    def storage(cls):
        if not hasattr(cls, '_storage'):
            cls._storage = cls()
            cls._storage.load(mobs_settings.MOBS_STORAGE)
        return cls._storage

    def get_available_mobs_list(self, level, terrain=None):
        mobs = []
        for mob_record in self.data.values():
            if mob_record.level <= level and (terrain is None or terrain in mob_record.terrain):
                mobs.append(mob_record)
        return mobs

    def get_mob(self, hero, mob_id):
        mob_record = self.data[mob_id]
        return MobPrototype(record=mob_record, level=hero.level)

    def get_random_mob(self, hero):
        mob_record = random.choice(self.get_available_mobs_list(level=hero.level, terrain=hero.position.get_terrain()))
        return MobPrototype(record=mob_record, level=hero.level)
