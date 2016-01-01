# coding: utf-8

from dext.common.utils import storage as dext_storage

from the_tale.game.persons import models
from the_tale.game.persons import exceptions
from the_tale.game.persons import relations


class PersonsStorage(dext_storage.Storage):
    SETTINGS_KEY = 'persons change time'
    EXCEPTION = exceptions.PersonsStorageError

    def _construct_object(self, model):
        from . import logic
        return logic.load_person(person_model=model)

    def _save_object(self, person):
        from . import logic
        return logic.save_person(person)

    def _get_all_query(self):
        return models.Person.objects.all()


persons = PersonsStorage()



class SocialConnectionsStorage(dext_storage.CachedStorage):
    SETTINGS_KEY = 'social-connections-storage'
    EXCEPTION = exceptions.PersonsStorageError

    def _construct_object(self, model):
        from the_tale.game.persons import logic
        return logic.social_connection_from_model(model)

    def _get_all_query(self):
        return models.SocialConnection.objects.filter(state=relations.SOCIAL_CONNECTION_STATE.IN_GAME)

    def _reset_cache(self):
        self._person_connections = {}

    def _update_cached_data(self, item):
        if item.person_1_id not in self._person_connections:
            self._person_connections[item.person_1_id] = {}

        if item.person_2_id not in self._person_connections:
            self._person_connections[item.person_2_id] = {}

        self._person_connections[item.person_1_id][item.person_2_id] = item
        self._person_connections[item.person_2_id][item.person_1_id] = item

    def get_person_connections(self, person):
        self.sync()
        connections = self._person_connections.get(person.id, {})

        result = []

        for connected_person_id, item in connections.iteritems():
            connected_person = persons.get(connected_person_id)
            if connected_person is None:
                continue
            result.append((item.connection, connected_person.id))

        return result

    def get_connected_persons_ids(self, person):
        self.sync()
        return self._person_connections.get(person.id, {}).keys()

    def is_connected(self, person_1, person_2):
        return person_2.id in self.get_connected_persons_ids(person_1)

    def get_connection_type(self, person_1, person_2):
        if not self.is_connected(person_1, person_2):
            return None
        return self._person_connections[person_1.id][person_2.id].connection



social_connections = SocialConnectionsStorage()
