# coding: utf-8

from dext.common.utils import storage as dext_storage

from the_tale.common.utils import storage

from the_tale.game.persons import models
from the_tale.game.persons import prototypes
from the_tale.game.persons import exceptions
from the_tale.game.persons import relations


class PersonsStorage(storage.Storage):
    SETTINGS_KEY = 'persons change time'
    EXCEPTION = exceptions.PersonsStorageError
    PROTOTYPE = prototypes.PersonPrototype

    def _get_all_query(self):
        return self.PROTOTYPE._db_exclude(state=relations.PERSON_STATE.REMOVED)

    def filter(self, place_id=None, state=None):
        return [person
                for person in self.all()
                if ((state is None or person.state==state) and
                    (place_id is None or place_id==person.place_id))]

    def remove_out_game_persons(self):
        from the_tale.game.bills.prototypes import BillPrototype
        from the_tale.game.heroes import logic as heroes_logic

        remove_time_border = min(BillPrototype.get_minimum_created_time_of_active_bills(),
                                 heroes_logic.get_minimum_created_time_of_active_quests())

        changed = False

        for person in self.all():
            if person.state == relations.PERSON_STATE.OUT_GAME and person.out_game_at < remove_time_border:
                person.remove_from_game()
                person.save()
                changed = True

        if changed:
            self.update_version()


    def get_total_power(self):
        return sum(person.power for person in self.filter(state=relations.PERSON_STATE.IN_GAME))

    def get_medium_power_for_person(self):
        persons_number = len(self.filter(state=relations.PERSON_STATE.IN_GAME))

        if persons_number == 0:
            return 0

        return self.get_total_power() / persons_number


persons_storage = PersonsStorage()



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
            connected_person = persons_storage.get(connected_person_id)
            if connected_person is None:
                continue
            if not connected_person.state.is_IN_GAME:
                continue
            result.append((item.connection, connected_person.id))

        return result

    def get_connected_persons_ids(self, person):
        self.sync()
        return [person_id
                for person_id in self._person_connections.get(person.id, {}).iterkeys()
                if persons_storage[person_id].state.is_IN_GAME]

    def is_connected(self, person_1, person_2):
        return person_2.id in self.get_connected_persons_ids(person_1)

    def get_connection_type(self, person_1, person_2):
        if not self.is_connected(person_1, person_2):
            return None
        return self._person_connections[person_1.id][person_2.id].connection



social_connections = SocialConnectionsStorage()
