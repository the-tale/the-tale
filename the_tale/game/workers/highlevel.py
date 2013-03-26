# coding: utf-8
import time
import datetime
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
from game.conf import game_settings
from game import signals as game_signals

class HighlevelException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, highlevel_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_highlevel'), command_queue=highlevel_queue)

    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def run(self):

        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)


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

        self.logger.info('HIGHLEVEL INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):

        settings.refresh()

        # check if new real day started
        if (time.time() - float(settings.get(game_settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY, 0)) > 23.5*60*60 and
            datetime.datetime.now().hour >= game_settings.REAL_DAY_STARTED_TIME):
            game_signals.day_started.send(self.__class__)
            settings[game_settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY] = str(time.time())

        # check if cleaning run needed
        if (time.time() - float(settings.get(game_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            datetime.datetime.now().hour >= game_settings.CLEANING_RUN_TIME):
            settings[game_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY] = str(time.time())
            self.supervisor_worker.cmd_run_cleaning()

        map_update_needed = False
        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise HighlevelException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))

            if self.turn_number % c.MAP_SYNC_TIME == 0:
                self.sync_data()
                map_update_needed = True

            if self.turn_number % (game_settings.RATINGS_SYNC_TIME / c.TURN_DELTA) == 0:
                self.supervisor_worker.cmd_recalculate_ratings()

            if self.turn_number % (bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA) == 0:
                if self.apply_bills():
                    map_update_needed = True

        if map_update_needed:
            subprocess.call(['./manage.py', 'map_update_map'])

            # send command to main supervisor queue
            self.supervisor_worker.cmd_highlevel_data_updated()

        # send command to supervisor answer queue
        self.supervisor_worker.cmd_answer('next_turn', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        with nested_commit_on_success():
            self.sync_data()

        subprocess.call(['./manage.py', 'map_update_map'])

        self.initialized = False

        self.supervisor_worker.cmd_answer('stop', self.worker_id)

        self.stop_required = True
        self.logger.info('HIGHLEVEL STOPPED')


    @places_storage.postpone_version_update
    @buildings_storage.postpone_version_update
    @persons_storage.postpone_version_update
    def sync_data(self):

        places_power_delta = {}

        for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):

            if person.id in self.persons_power:
                person.push_power(self.turn_number, self.persons_power[person.id])

                if person.place_id not in places_power_delta:
                    places_power_delta[person.place_id] = 0

                places_power_delta[person.place_id] += self.persons_power[person.id]

            person.update_friends_number()
            person.update_enemies_number()

        self.persons_power = {}

        max_place_power = 0

        # calculate power
        for place in places_storage.all():
            place.push_power(self.turn_number, places_power_delta.get(place.id, 0))
            max_place_power = max(max_place_power, place.power)

        # update size
        places_by_power = sorted(places_storage.all(), key=lambda x: x.power)
        places_number = len(places_by_power)
        for i, place in enumerate(places_by_power):
            new_size = int(places_settings.MAX_SIZE * float(i) / places_number) + 1
            if place.modifier:
                new_size = place.modifier.modify_place_size(new_size)

            if new_size > place.size:
                place.size += 1
            elif new_size < place.size:
                place.size -= 1

        # update places
        for place in places_storage.all():
            place.sync_persons()
            place.update_heroes_number()
            place.sync_modifier()
            place.mark_as_updated()

        places_storage.save_all()

        persons_storage.remove_out_game_persons()
        persons_storage.save_all()

        for building in buildings_storage.all():
            building.amortize(c.MAP_SYNC_TIME)

        buildings_storage.save_all()

    def apply_bills(self):
        import datetime
        from game.bills.models import Bill, BILL_STATE
        from game.bills.prototypes import BillPrototype

        bills_models = Bill.objects.filter(state=BILL_STATE.VOTING,
                                           approved_by_moderator=True,
                                           updated_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME))

        applied = False

        for bill_model in bills_models:
            bill = BillPrototype(bill_model)
            applied = bill.apply() or applied

        return applied


    def cmd_change_person_power(self, person_id, power_delta):
        self.send_cmd('change_person_power', {'person_id': person_id, 'power_delta': power_delta})

    def process_change_person_power(self, person_id, power_delta):
        person_power = self.persons_power.get(person_id, 0)
        self.persons_power[person_id] = person_power + power_delta

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id):
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, highlevel=self)
        task.do_postsave_actions()
