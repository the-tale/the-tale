
import smart_imports

smart_imports.all()


class EmissariesStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'emissaries change time'
    EXCEPTION = exceptions.EmissariesStorageError

    def _construct_object(self, model):
        return logic.load_emissary(emissary_model=model)

    def _save_object(self, emissary):
        return logic.save_emissary(emissary)

    def _get_all_query(self):
        return models.Emissary.objects.filter(state=relations.STATE.IN_GAME)

    def _reset_cache(self):
        self._emissaries_by_clan = {}

    def _update_cached_data(self, item):
        if item.clan_id not in self._emissaries_by_clan:
            self._emissaries_by_clan[item.clan_id] = []

        self._emissaries_by_clan[item.clan_id].append(item)

    @property
    def emissaries_by_clan(self):
        self.sync()
        return self._emissaries_by_clan

    def get_or_load(self, emissary_id):
        if emissary_id in self:
            return self[emissary_id]

        return logic.load_emissary(emissary_id=emissary_id)


emissaries = EmissariesStorage()


class EventsStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'events change time'
    EXCEPTION = exceptions.EventsStorageError

    def _construct_object(self, model):
        return logic.load_event(event_model=model)

    def _save_object(self, event):
        return logic.save_event(event)

    def _get_all_query(self):
        return models.Event.objects.filter(state=relations.EVENT_STATE.RUNNING)

    def _reset_cache(self):
        self._events_by_emissary = {}

    def _update_cached_data(self, item):
        if item.emissary_id not in self._events_by_emissary:
            self._events_by_emissary[item.emissary_id] = []

        self._events_by_emissary[item.emissary_id].append(item)

    def emissary_events(self, emissary_id):
        self.sync()
        return self._events_by_emissary.get(emissary_id, ())

    def clan_events(self, clan_id):
        self.sync()

        events = []

        for emissary in emissaries.emissaries_by_clan[clan_id]:
            for event in self._events_by_emissary.get(emissary.id, ()):
                events.append(event)

        return events

    def get_or_load(self, event_id):
        if event_id in self:
            return self[event_id]

        return logic.load_event(event_id=event_id)


events = EventsStorage()
