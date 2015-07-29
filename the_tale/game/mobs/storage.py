# coding: utf-8
import random

from the_tale.common.utils import storage
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.mobs import exceptions
from the_tale.game.mobs.prototypes import MobPrototype, MobRecordPrototype
from the_tale.game.mobs import relations


class MobsStorage(storage.CachedStorage):
    SETTINGS_KEY = 'mob records change time'
    EXCEPTION = exceptions.MobsStorageError
    PROTOTYPE = MobRecordPrototype

    def _update_cached_data(self, item):
        self._mobs_by_uuids[item.uuid] = item
        self._types_count[item.type] = len([mob for mob in self.all() if mob.type == item.type])
        self.mobs_number = len(self.all())

    def _reset_cache(self):
        self._mobs_by_uuids = {}
        self._types_count = {mob_type: 0 for mob_type in relations.MOB_TYPE.records}
        self.mobs_number = 0

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


    def choose_mob(self, mobs_choices):
        global_actions_mobs = []
        normal_mobs = []

        for mob in mobs_choices:
            if mob.global_action_probability > 0:
                global_actions_mobs.append(mob)
            else:
                normal_mobs.append(mob)

        action_probability = sum(mob.global_action_probability for mob in global_actions_mobs if mob.global_action_probability)

        if random.random() > action_probability:
            return random.choice(normal_mobs)

        return random_value_by_priority((mob, mob.global_action_probability) for mob in global_actions_mobs)


    def get_random_mob(self, hero, mercenary=None, is_boss=False):
        self.sync()

        choices = self.get_available_mobs_list(level=hero.level, terrain=hero.position.get_terrain(), mercenary=mercenary)

        if not choices:
            return None

        mob_record = self.choose_mob(choices)

        return MobPrototype(record_id=mob_record.id, level=hero.level, is_boss=is_boss, action_type=hero.actions.current_action.ui_type, terrain=hero.position.get_terrain())

    def create_mob_for_hero(self, hero):
        return self.get_random_mob(hero)


mobs_storage = MobsStorage()
