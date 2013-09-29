# coding: utf-8
import subprocess

from dext.settings import settings

from django.utils.log import getLogger

from dext.utils.decorators import nested_commit_on_success

from common.amqp_queues import BaseWorker
from common import postponed_tasks

from game.balance import constants as c

from game.persons.models import PERSON_STATE
from game.persons.storage import persons_storage

from game.map.places.storage import places_storage, buildings_storage
from game.map.places.conf import places_settings

from game.bills.conf import bills_settings
from game.workers.environment import workers_environment as game_environment

from game import exceptions


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_highlevel')
    name = 'game highlevel'
    command_name = 'game_highlevel'
    stop_signal_required = False

    def __init__(self, highlevel_queue):
        super(Worker, self).__init__(command_queue=highlevel_queue)

    run = BaseWorker.run_simple

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            self.logger.warn('highlevel already initialized, do reinitialization')

        postponed_tasks.autodiscover()

        self.initialized = True
        self.worker_id = worker_id
        self.turn_number = turn_number
        self.persons_power = {}
        self.places_power = {}

        self.logger.info('HIGHLEVEL INITIALIZED')

        game_environment.supervisor.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        settings.refresh()

        map_update_needed = False
        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise exceptions.WrongHighlevelTurnNumber(expected_turn_number=self.turn_number, new_turn_number=turn_number)

            if self.turn_number % c.MAP_SYNC_TIME == 0:
                self.sync_data()
                map_update_needed = True

            if self.turn_number % (bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA) == 0:
                if self.apply_bills():
                    map_update_needed = True

        if map_update_needed:
            self.logger.info('update map')
            subprocess.call(['./manage.py', 'map_update_map'])
            self.logger.info('update map completed')

            # send command to main supervisor queue
            game_environment.supervisor.cmd_highlevel_data_updated()

        # send command to supervisor answer queue
        game_environment.supervisor.cmd_answer('next_turn', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        with nested_commit_on_success():
            self.sync_data()

        subprocess.call(['./manage.py', 'map_update_map'])

        self.initialized = False

        game_environment.supervisor.cmd_answer('stop', self.worker_id)

        self.stop_required = True
        self.logger.info('HIGHLEVEL STOPPED')


    @places_storage.postpone_version_update
    @buildings_storage.postpone_version_update
    @persons_storage.postpone_version_update
    def sync_data(self):

        self.logger.info('sync data')

        places_power_delta = {}

        for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):

            if person.id in self.persons_power:

                power_multiplier = 1
                if person.has_building:
                    power_multiplier *= c.BUILDING_PERSON_POWER_MULTIPLIER

                power = self.persons_power[person.id] * power_multiplier * person.place.freedom

                person.push_power(self.turn_number, power)

                if person.place_id not in places_power_delta:
                    places_power_delta[person.place_id] = 0

                places_power_delta[person.place_id] += power

            person.update_friends_number()
            person.update_enemies_number()

        self.persons_power = {}

        for place_id, power in self.places_power.iteritems():
            place = places_storage[place_id]

            if place_id not in places_power_delta:
                places_power_delta[place_id] = 0

            places_power_delta[place_id] += power * place.freedom

        self.places_power = {}

        max_place_power = 0

        # calculate power
        for place in places_storage.all():
            place.push_power(self.turn_number, places_power_delta.get(place.id, 0))
            max_place_power = max(max_place_power, place.power)

        # update size
        places_by_power = sorted(places_storage.all(), key=lambda x: x.power)
        places_number = len(places_by_power)
        for i, place in enumerate(places_by_power):
            expected_size = int(places_settings.MAX_SIZE * float(i) / places_number) + 1
            if place.modifier:
                expected_size = place.modifier.modify_economic_size(expected_size)
            place.set_expected_size(expected_size)

            place.sync_size(c.MAP_SYNC_TIME_HOURS)
            place.sync_persons()
            place.sync_modifier()
            place.sync_parameters() # must be last operation to display and use real data

            place.update_heroes_number()
            place.mark_as_updated()

        places_storage.save_all()

        persons_storage.remove_out_game_persons()
        persons_storage.save_all()

        for building in buildings_storage.all():
            building.amortize(c.MAP_SYNC_TIME)

        buildings_storage.save_all()

        self.logger.info('sync data completed')

    def apply_bills(self):
        from game.bills.prototypes import BillPrototype

        self.logger.info('apply bills')

        applied = False

        for bill in BillPrototype.get_applicable_bills():
            applied = bill.apply() or applied

        for bill in BillPrototype.get_bills_to_end():
            applied = bill.end() or applied

        self.logger.info('apply bills completed')

        return applied


    def cmd_change_power(self, person_id, place_id, power_delta):
        self.send_cmd('change_power', {'person_id': person_id, 'place_id': place_id, 'power_delta': power_delta})

    def process_change_power(self, person_id, place_id, power_delta):
        if person_id is not None and place_id is None:
            person_power = self.persons_power.get(person_id, 0)
            self.persons_power[person_id] = person_power + power_delta
        elif place_id is not None and person_id is None:
            place_power = self.places_power.get(place_id, 0)
            self.places_power[place_id] = place_power + power_delta
        else:
            raise exceptions.ChangePowerError(place_id=place_id, person_id=person_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        settings.refresh()

        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, highlevel=self)
        task.do_postsave_actions()
