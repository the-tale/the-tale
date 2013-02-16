# coding: utf-8
import random

from common.utils.storage import create_storage_class

from game.mobs.exceptions import MobsException
from game.mobs.prototypes import MobPrototype, MobRecordPrototype
from game.mobs.models import MobRecord

class MobsStorage(create_storage_class('mob records change time', MobRecord, MobRecordPrototype, MobsException)):

    def refresh(self):
        super(MobsStorage, self).refresh()
        self._mobs_by_uuids = dict( (mob.uuid, mob) for mob in self.all())

    def get_by_uuid(self, uuid):
        self.sync()
        return self._mobs_by_uuids.get(uuid)

    def has_mob(self, uuid):
        self.sync()
        return uuid in self._mobs_by_uuids

    def get_available_mobs_list(self, level, terrain=None):
        self.sync()
        return [record
                for record in self.all()
                if record.state.is_enabled and record.level <= level and (terrain is None or terrain in record.terrains)]

    def get_random_mob(self, hero):
        self.sync()
        mob_record = random.choice(self.get_available_mobs_list(level=hero.level, terrain=hero.position.get_terrain()))
        return MobPrototype(record=mob_record, level=hero.level)

mobs_storage = MobsStorage()
