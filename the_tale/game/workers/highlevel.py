# coding: utf-8

from django.db import transaction

from the_tale.amqp_environment import environment

from the_tale.common.utils.workers import BaseWorker
from the_tale.common import postponed_tasks

from the_tale.game.balance import constants as c

from the_tale.game.bills import prototypes as bill_prototypes

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic

from the_tale.game.places import storage as places_storage

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

        self.persons_politic_power = []
        self.places_politic_power = []

        self.logger.info('HIGHLEVEL INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        sync_data_sheduled = None
        sync_data_required = False

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
            with transaction.atomic():
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


    def sync_sizes(self, places, hours, max_size):
        if not places:
            return

        places = sorted(places, key=lambda x: x.power)
        places_number = len(places)

        for i, place in enumerate(places):
            place.attrs.set_power_economic(int(max_size * float(i) / places_number) + 1)
            place.attrs.sync_size(hours)


    @places_storage.places.postpone_version_update
    @places_storage.buildings.postpone_version_update
    @persons_storage.persons.postpone_version_update
    def sync_data(self, sheduled=True):

        self.logger.info('sync data')

        for person_id, hero_id, has_place_in_preferences, has_person_in_preferences, power_delta in self.persons_politic_power:
            person = persons_storage[person_id]
            place_power = person.politic_power.change_power(person=person,
                                                            hero_id=hero_id,
                                                            has_in_preferences=has_person_in_preferences,
                                                            power=power_delta)
            self.places_politic_power.append(person.place.id, hero_id, has_place_in_preferences, has_person_in_preferences, place_power)

        for place_id, hero_id, has_place_in_preferences, has_person_in_preferences, power_delta in self.places_politic_power:
            place = places_storage[place_id]
            place.politic_power.change_power(place=place,
                                             hero_id=hero_id,
                                             has_in_preferences=has_place_in_preferences,
                                             power=power_delta)

        self.persons_politic_power[:] = []
        self.places_politic_power[:] = []

        for person in persons_storage.persons.all():
            if sheduled:
                person.politic_power.sync_power()

            person.update_friends_number()
            person.update_enemies_number()


        for place in places_storage.places.all():
            if sheduled:
                place.politic_power.sync_power()

        # update size
        if sheduled:
            self.sync_sizes([place for place in places_storage.places.all() if place.is_frontier],
                            hours=c.MAP_SYNC_TIME_HOURS,
                            max_size=c.PLACE_MAX_FRONTIER_SIZE)

            self.sync_sizes([place for place in places_storage.places.all() if not place.is_frontier],
                            hours=c.MAP_SYNC_TIME_HOURS,
                            max_size=c.PLACE_MAX_SIZE)


        for place in places_storage.places.all():
            if sheduled:
                place.effects.update_step(place)

            place.sync_habits()

            place.refresh_attributes() # must be last operation to display and use real data

            place.update_heroes_number()
            place.update_heroes_habits()

            place.mark_as_updated()

        places_storage.places.save_all()

        persons_storage.persons.save_all()

        persons_logic.sync_social_connections()

        if sheduled:
            for building in places_storage.buildings.all():
                building.amortize(c.MAP_SYNC_TIME)

        places_storage.buildings.save_all()

        self.logger.info('sync data completed')


    def apply_bills(self):
        self.logger.info('apply bills')

        applied = False

        for applied_bill_id in bill_prototypes.BillPrototype.get_applicable_bills_ids():
            bill = bill_prototypes.BillPrototype.get_by_id(applied_bill_id)
            if bill.state.is_VOTING:
                applied = bill.apply() or applied

            for active_bill_id in bill_prototypes.BillPrototype.get_active_bills_ids():
                bill = bill_prototypes.BillPrototype.get_by_id(active_bill_id)
                if not bill.has_meaning():
                    bill.stop()

        self.logger.info('apply bills completed')

        return applied

    def _change_power(self, storage, id_, power_delta):
        power_good, power_bad = storage.get(id_, (0, 0))
        storage[id_] = (power_good + (power_delta if power_delta > 0 else 0),
                        power_bad + (power_delta if power_delta < 0 else 0))


    def cmd_change_power(self, hero_id, has_place_in_preferences, has_person_in_preferences, person_id, place_id, power_delta):
        self.send_cmd('change_power', {'hero_id': hero_id,
                                       'has_place_in_preferences': has_place_in_preferences,
                                       'has_person_in_preferences': has_person_in_preferences,
                                       'person_id': person_id,
                                       'place_id': place_id,
                                       'power_delta': power_delta})

    def process_change_power(self, hero_id, has_place_in_preferences, has_person_in_preferences, person_id, place_id, power_delta):
        if person_id is not None and place_id is None:
            self.persons_politic_power.append((person_id, hero_id, has_place_in_preferences, has_person_in_preferences, power_delta))
        elif place_id is not None and person_id is None:
            self.places_politic_power.append((place_id, hero_id, has_place_in_preferences, has_person_in_preferences, power_delta))
        else:
            raise exceptions.ChangePowerError(place_id=place_id, person_id=person_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, highlevel=self)
        task.do_postsave_actions()
