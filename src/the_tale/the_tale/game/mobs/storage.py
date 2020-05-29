

import smart_imports

smart_imports.all()


class MobsStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'mob records change time'
    EXCEPTION = exceptions.MobsStorageError

    def _construct_object(self, model):
        return logic.construct_from_model(model)

    def _get_all_query(self):
        return models.MobRecord.objects.all()

    def _update_cached_data(self, item):
        self._mobs_by_uuids[item.uuid] = item
        self._types_count[item.type] = len([mob for mob in self.all() if mob.type == item.type])
        self.mobs_number = len(self.all())

    def _reset_cache(self):
        self._mobs_by_uuids = {}
        self._types_count = {mob_type: 0 for mob_type in tt_beings_relations.TYPE.records}
        self.mobs_number = 0

    def get_by_uuid(self, uuid):
        self.sync()
        return self._mobs_by_uuids.get(uuid)

    def has_mob(self, uuid):
        self.sync()
        return uuid in self._mobs_by_uuids

    def mob_type_fraction(self, mob_type): return self._types_count[mob_type] / float(self.mobs_number)

    def get_all_mobs_for_level(self, level):
        self.sync()
        return [mob for mob in self.all() if mob.state.is_ENABLED and mob.level <= level]

    def _get_mobs_choices(self, level, terrain, mercenary):
        self.sync()

        mobs = ((mob, 1) for mob in self.all() if mob.state.is_ENABLED)

        mobs = filters.restrict_level(mobs, level=level)

        mobs = filters.restrict_terrain(mobs, terrain)

        if mercenary is not None:
            mobs = filters.restrict_mercenary(mobs, mercenary)

        # first april joke
        # mobs = filters.change_type_priority(mobs, types=(tt_beings_relations.TYPE.UNDEAD,), delta=7)

        return mobs

    def get_random_mob(self, hero, mercenary=None, is_boss=False):
        self.sync()

        mobs = self._get_mobs_choices(level=hero.level,
                                      terrain=hero.position.cell().terrain,
                                      mercenary=mercenary)

        if not mobs:
            return None

        mob_record = utils_logic.random_value_by_priority(mobs)

        return objects.Mob(record_id=mob_record.id,
                           level=hero.level,
                           is_boss=is_boss,
                           action_type=hero.actions.current_action.ui_type,
                           terrain=hero.position.cell().terrain)

    def create_mob_for_hero(self, hero):
        return self.get_random_mob(hero)


mobs: MobsStorage = MobsStorage()
