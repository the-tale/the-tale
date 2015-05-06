# coding: utf-8

from django.db import transaction

from the_tale.amqp_environment import environment

from the_tale.common.utils.workers import BaseWorker
from the_tale.common import postponed_tasks

from the_tale.game.balance import constants as c

from the_tale.game.persons.relations import PERSON_STATE
from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic

from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.map.places.conf import places_settings

from the_tale.game.bills.conf import bills_settings

from the_tale.game import exceptions


E = 0.001


class Worker(BaseWorker):
    STOP_SIGNAL_REQUIRED = False

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            self.logger.warn('highlevel already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id
        self.turn_number = turn_number
        self.persons_power = {}
        self.places_power = {}

        self.logger.info('HIGHLEVEL INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        sync_data_sheduled = None
        sync_data_required = False

        with transaction.atomic():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise exceptions.WrongHighlevelTurnNumber(expected_turn_number=self.turn_number, new_turn_number=turn_number)

            if self.turn_number % c.MAP_SYNC_TIME == 0:
                sync_data_required = True
                sync_data_sheduled = True

            if self.turn_number % (bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA) == 0:
                if self.apply_bills():
                    sync_data_required = True
                    sync_data_sheduled = False

        if sync_data_required:
            self.sync_data(sheduled=sync_data_sheduled)
            self.update_map()

    def update_map(self):
        self.logger.info('initialize map update')
        environment.workers.game_long_commands.cmd_update_map()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        with transaction.atomic():
            self.sync_data()

        self.initialized = False

        environment.workers.supervisor.cmd_answer('stop', self.worker_id)

        self.stop_required = True
        self.logger.info('HIGHLEVEL STOPPED')

    def get_power_correction(self, positive_power, negative_power):
        # if positive_power / negative_power < relation
        # (positive_power + x) / negative_power = relation
        # x = relation * negative_power - positive_power
        #
        # if positive_power / negative_power > relation
        # positive_power / (negative_power + x) = relation
        # (positive_power - negative_power * relation) / reltation = x

        positive_power = abs(float(positive_power))
        negative_power = abs(float(negative_power))

        if negative_power > E and positive_power / negative_power < c.POSITIVE_NEGATIVE_POWER_RELATION:
            return c.POSITIVE_NEGATIVE_POWER_RELATION * negative_power - positive_power, 0.0

        return 0.0, (positive_power - negative_power * c.POSITIVE_NEGATIVE_POWER_RELATION) / c.POSITIVE_NEGATIVE_POWER_RELATION


    def sync_persons_powers(self, persons):
        if not persons:
            return

        total_positive_power = 0
        total_negative_power = 0

        for person in persons:

            if person.id not in self.persons_power:
                continue

            positive_power, negative_power, positive_bonus, negative_bonus = self.persons_power[person.id]

            power_multiplier = 1
            if person.has_building:
                power_multiplier *= c.BUILDING_PERSON_POWER_MULTIPLIER

            # this power will go to person and to place
            positive_power *= (1 + person.power_positive) * power_multiplier
            negative_power *= (1 + person.power_negative) * power_multiplier

            # this power, only to person
            power = (positive_power + negative_power) * person.place.freedom

            total_positive_power += positive_power * person.place.freedom
            total_negative_power += negative_power * person.place.freedom

            person.push_power(self.turn_number, power)
            person.push_power_positive(self.turn_number, positive_bonus)
            person.push_power_negative(self.turn_number, negative_bonus)

            self.change_place_power(person.place_id, 0, 0, positive_power)
            self.change_place_power(person.place_id, 0, 0, negative_power)


        person_positive_delta, person_negative_delta = self.get_power_correction(total_positive_power, total_negative_power)
        person_power_delta = (person_positive_delta - person_negative_delta) / len(persons)

        for person in persons:
            person.push_power(self.turn_number, person_power_delta)


    def sync_places_powers(self, places):

        if not places:
            return

        total_positive_power = 0
        total_negative_power = 0

        for place in places:

            if place.id not in self.places_power:
                continue

            positive_power, negative_power, positive_bonus, negative_bonus = self.places_power[place.id]

            positive_power *= (1 + place.power_positive)
            negative_power *= (1 + place.power_negative)

            power = (positive_power + negative_power) * place.freedom

            total_positive_power += positive_power * place.freedom
            total_negative_power += negative_power * place.freedom

            place.push_power(self.turn_number, power)
            place.push_power_positive(self.turn_number, positive_bonus)
            place.push_power_negative(self.turn_number, negative_bonus)

        place_positive_delta, place_negative_delta = self.get_power_correction(total_positive_power, total_negative_power)
        place_power_delta = (place_positive_delta - place_negative_delta) / len(places)

        for place in places:
            place.push_power(self.turn_number, place_power_delta)


    def sync_sizes(self, places, hours, max_size):
        if not places:
            return

        places = sorted(places, key=lambda x: x.raw_power)
        places_number = len(places)

        for i, place in enumerate(places):
            expected_size = int(max_size * float(i) / places_number) + 1

            if place.modifier:
                expected_size = place.modifier.modify_economic_size(expected_size)

            place.set_expected_size(expected_size)
            place.sync_size(hours)
            place.sync_persons(force_add=False)


    @places_storage.postpone_version_update
    @buildings_storage.postpone_version_update
    @persons_storage.persons_storage.postpone_version_update
    def sync_data(self, sheduled=True):

        self.logger.info('sync data')

        all_persons = persons_storage.persons_storage.filter(state=PERSON_STATE.IN_GAME)

        self.sync_persons_powers(persons=[person for person in all_persons if person.place.is_frontier])
        self.sync_persons_powers(persons=[person for person in all_persons if not person.place.is_frontier])

        for person in all_persons:
            person.update_friends_number()
            person.update_enemies_number()

        self.persons_power = {}

        self.sync_places_powers(places=[place for place in places_storage.all() if place.is_frontier])
        self.sync_places_powers(places=[place for place in places_storage.all() if not place.is_frontier])

        self.places_power = {}

        # update size
        if sheduled:
            self.sync_sizes([place for place in places_storage.all() if place.is_frontier],
                            hours=c.MAP_SYNC_TIME_HOURS,
                            max_size=places_settings.MAX_FRONTIER_SIZE)

            self.sync_sizes([place for place in places_storage.all() if not place.is_frontier],
                            hours=c.MAP_SYNC_TIME_HOURS,
                            max_size=places_settings.MAX_SIZE)


        for place in places_storage.all():
            place.sync_stability()
            place.sync_modifier()
            place.sync_habits()

            place.sync_parameters() # must be last operation to display and use real data

            place.update_heroes_number()
            place.update_heroes_habits()

            place.mark_as_updated()

        places_storage.save_all()

        persons_storage.persons_storage.remove_out_game_persons()
        persons_storage.persons_storage.save_all()

        persons_logic.sync_social_connections()

        if sheduled:
            for building in buildings_storage.all():
                building.amortize(c.MAP_SYNC_TIME)

        buildings_storage.save_all()

        self.logger.info('sync data completed')


    def apply_bills(self):
        from the_tale.game.bills.prototypes import BillPrototype

        self.logger.info('apply bills')

        applied = False

        for bill in BillPrototype.get_applicable_bills():
            applied = bill.apply() or applied

        for bill in BillPrototype.get_bills_to_end():
            applied = bill.end() or applied

        self.logger.info('apply bills completed')

        return applied

    def _change_power(self, storage, id_, positive_bonus_delta, negative_bonus_delta, power_delta):
        power_good, power_bad, positive_bonus, negative_bonus = storage.get(id_, (0, 0, 0, 0))
        storage[id_] = (power_good + (power_delta if power_delta > 0 else 0),
                        power_bad + (power_delta if power_delta < 0 else 0),
                        positive_bonus + positive_bonus_delta,
                        negative_bonus + negative_bonus_delta)

    def change_person_power(self, id_, positive_bonus, negative_bonus, power_delta):
        self._change_power(self.persons_power, id_, positive_bonus, negative_bonus, power_delta)

    def change_place_power(self, id_, positive_bonus, negative_bonus, power_delta):
        self._change_power(self.places_power, id_, positive_bonus, negative_bonus, power_delta)


    def cmd_change_power(self, person_id, positive_bonus, negative_bonus, place_id, power_delta):
        self.send_cmd('change_power', {'person_id': person_id,
                                       'positive_bonus': positive_bonus,
                                       'negative_bonus': negative_bonus,
                                       'place_id': place_id,
                                       'power_delta': power_delta})

    def process_change_power(self, person_id, positive_bonus, negative_bonus, place_id, power_delta):
        if person_id is not None and place_id is None:
            self.change_person_power(person_id, positive_bonus, negative_bonus, power_delta)
        elif place_id is not None and person_id is None:
            self.change_place_power(place_id, positive_bonus, negative_bonus, power_delta)
        else:
            raise exceptions.ChangePowerError(place_id=place_id, person_id=person_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, highlevel=self)
        task.do_postsave_actions()
