# coding: utf-8
import traceback
import subprocess

from django_next.utils.decorators import nested_commit_on_success

from ..persons.models import Person, PERSON_STATE
from ..persons.prototypes import get_person_by_model
from ..map.places.models import Place
from ..map.places.prototypes import get_place_by_model

SYNC_DELTA = 300 # in turns

class CMD_TYPE:
    INITIALIZE = 'initialize'
    NEXT_TURN = 'next_turn'
    CHANGE_PERSON_POWER = 'change_person_power'

class HighlevelException(Exception): pass

class Worker(object):

    def __init__(self, connection, highlevel_queue):
        self.highlevel_queue = connection.SimpleQueue(highlevel_queue)
        self.exception_raised = False
        self.stop_required = False
        self.initialized = False
        print 'HIGHLEVEL CONSTRUCTED'

    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def close_queries(self):
        self.highlevel_queue.close()

    def clean_queues(self):
        self.highlevel_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            cmd = self.highlevel_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        print '<%s> %r' % (cmd_type, cmd_data)

        try:
            { CMD_TYPE.INITIALIZE: self.process_initialize,
              CMD_TYPE.NEXT_TURN: self.process_next_turn,
              CMD_TYPE.CHANGE_PERSON_POWER: self.process_change_person_power,}[cmd_type](**cmd_data)
        except Exception, e:
            self.exception_raised = True
            print 'EXCEPTION: %s' % e
            traceback.print_exc()

    def send_cmd(self, tp, data={}):
        self.highlevel_queue.put({'type': tp, 'data': data}, serializer='json', compression=None)

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd(CMD_TYPE.INITIALIZE, {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):
        
        if self.initialized:
            print 'WARNING: highlevel already initialized, do reinitialization'

        self.initialized = True
        self.worker_id = worker_id
        self.turn_number = turn_number
        self.persons_power = {}

        print 'HIGHLEVEL INITIALIZED'

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)


    def cmd_next_turn(self, turn_number):
        return self.send_cmd(CMD_TYPE.NEXT_TURN, data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):
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

    def sync_data(self):

        for person_model in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            person = get_person_by_model(person_model)
            
            if person.id in self.persons_power:
                person.power = max(person.power + self.persons_power[person.id], 0)

            person.save()
            
        old_powers = self.persons_power

        self.persons_power = {}

        places = []

        max_place_power = 0

        for place_model in Place.objects.all():
            place = get_place_by_model(place_model)
            place.sync_power(old_powers)
            place.sync_terrain()
            places.append(place)

            max_place_power = max(max_place_power, place.power)

        for place in places:
            place.sync_size(max_place_power)
            place.sync_persons()
            place.save()


    def cmd_change_person_power(self, person_id, power_delta):
        self.send_cmd(CMD_TYPE.CHANGE_PERSON_POWER, {'person_id': person_id, 'power_delta': power_delta})

    def process_change_person_power(self, person_id, power_delta):
        person_power = self.persons_power.get(person_id, 0)
        self.persons_power[person_id] = max(person_power + power_delta, 0)

