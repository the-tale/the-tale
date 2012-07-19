# coding: utf-8
import subprocess

from dext.settings import settings

from django.utils.log import getLogger

from dext.utils.decorators import nested_commit_on_success

from common.amqp_queues import BaseWorker

from game.persons.models import Person, PERSON_STATE
from game.persons.storage import persons_storage
from game.map.places.storage import places_storage

SYNC_DELTA = 300 # in turns

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

        map_update_needed = False
        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise HighlevelException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))

            if self.turn_number % SYNC_DELTA == 0:
                self.sync_data()
                map_update_needed = True

        if map_update_needed:
            subprocess.call(['./manage.py', 'map_update_map'])

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


    def sync_data(self):

        persons_ids = Person.objects.filter(state=PERSON_STATE.IN_GAME).values_list('id', flat=True)

        for person_id in persons_ids:
            person = persons_storage[person_id]

            if person.id in self.persons_power:
                person.power = max(person.power + self.persons_power[person.id], 0)

            person.save()

        old_powers = self.persons_power

        self.persons_power = {}

        places = []

        max_place_power = 0

        for place in places_storage.all():
            place.sync_power(self.turn_number, old_powers)
            place.sync_terrain()
            places.append(place)

            max_place_power = max(max_place_power, place.power)

        for place in places:
            place.sync_size(max_place_power)
            place.sync_persons()

        places_storage.save_all()


    def cmd_change_person_power(self, person_id, power_delta):
        self.send_cmd('change_person_power', {'person_id': person_id, 'power_delta': power_delta})

    def process_change_person_power(self, person_id, power_delta):
        person_power = self.persons_power.get(person_id, 0)
        self.persons_power[person_id] = max(person_power + power_delta, 0)
