# coding: utf-8
import random

from the_tale.common.utils.storage import create_storage_class

from the_tale.game.mobs import exceptions
from the_tale.game.mobs.prototypes import MobPrototype, MobRecordPrototype
from the_tale.game.mobs import relations


class MobsStorage(create_storage_class('mob records change time', MobRecordPrototype, exceptions.MobsStorageError)):

    def __init__(self):
        super(MobsStorage, self).__init__()
        self._mobs_by_uuids = {}
        self._types_count = {mob_type: 0 for mob_type in relations.MOB_TYPE.records}
        self.mobs_number = 0

    def update_cached_data(self, item):
        self._mobs_by_uuids[item.uuid] = item
        self._types_count[item.type] += 1
        self.mobs_number += 1

    def clear(self):
        super(MobsStorage, self).clear()
        self._mobs_by_uuids = {}
        self._types_count = {mob_type: 0 for mob_type in relations.MOB_TYPE.records}
        self.mobs_number = 0

    def add_item(self, id_, item):
        super(MobsStorage, self).add_item(id_, item)
        self.update_cached_data(item)

    def get_by_uuid(self, uuid):
        self.sync()
        return self._mobs_by_uuids.get(uuid)

    def has_mob(self, uuid):
        self.sync()
        return uuid in self._mobs_by_uuids

    def mob_type_fraction(self, mob_type): return self._types_count[mob_type] / float(self.mobs_number)

    def get_available_mobs_list(self, level, terrain=None, mercenary=None):
        self.sync()

        mobs = (record
                for record in self.all()
                if record.state.is_ENABLED and record.level <= level and (terrain is None or terrain in record.terrains))

        if mercenary is not None:
            mobs = (record for record in mobs if record.type.is_mercenary == mercenary)

        return list(mobs)


    def get_random_mob(self, hero, mercenary=None, is_boss=False):
        self.sync()

        choices = self.get_available_mobs_list(level=hero.level, terrain=hero.position.get_terrain(), mercenary=mercenary)

        if not choices:
            return None

        mob_record = random.choice(choices)
        return MobPrototype(record=mob_record, level=hero.level, is_boss=is_boss)

mobs_storage = MobsStorage()
