# coding: utf-8
import subprocess

from celery.task import Task

from django_next.utils.decorators import nested_commit_on_success

from ..persons.models import Person
from ..persons.prototypes import get_person_by_model
from ..map.places.models import Place
from ..map.places.prototypes import get_place_by_model

class HighlevelException(Exception): pass

class TASK_TYPE:
    INITIALIZE = 'initialize'
    NEXT_TURN = 'next_turn'
    CHANGE_PERSON_POWER = 'change_person_power'

SYNC_DELTA = 100 # in turns

class highlevel(Task):

    name = 'highlevel'
    exchange = 'highlevel'
    routing_key = 'highlevel.cmd'

    def __init__(self):
        print 'CONSTRUCT HIGHLEVEL'
        self.initialized = False
        self.exception_raised = False

    def initialize(self):
        print 'INIT HIGHLEVEL'
        self.initialized = True
        
        self.turn_number = 0
        self.persons_power = {}

    def sync_data(self):
        
        for place_model in Place.objects.all():
            place = get_place_by_model(place_model)
            place.sync_persons()
            place.sync_terrain()
            place.save()

        for person_model in Person.objects.all():
            person = get_person_by_model(person_model)
            
            if person.id in self.persons_power:
                person.power = max(person.power + self.persons_power[person.id], 0)

            person.save()

        self.persons_power = {}

        subprocess.call(['./manage.py', 'map_update_map'])

    def log_cmd(self, cmd, params):
        print 'highlevel: %s %r' % (cmd, params)

    def run(self, cmd, params):

        try:

            if self.exception_raised:
                print 'skip command becouse of exception'
                return 0

            if not self.initialized:
                self.initialize()

            self.log_cmd(cmd, params)
        
            if cmd == TASK_TYPE.INITIALIZE:
                self.turn_number = params['turn_number']

            elif cmd == TASK_TYPE.NEXT_TURN:
                steps_delta = params['steps_delta']

                while steps_delta:
                    self.turn_number += 1

                    steps_delta -= 1

                    if self.turn_number % SYNC_DELTA == 0:
                        with nested_commit_on_success():
                            self.sync_data()

            elif cmd == TASK_TYPE.CHANGE_PERSON_POWER:
                person_id = int(params['person_id'])
                power_delta = int(params['power_delta'])
                
                person_power = self.persons_power.get(person_id, 0)
                self.persons_power[person_id] = max(person_power + power_delta, 0)

        except:
            self.exception_raised = True
            raise

        return 0
    
    @classmethod
    def _do_task(cls, cmd, args):
        return cls.apply_async(args=[cmd, args])

    @classmethod
    def cmd_initialize(cls, turn_number):
        return cls._do_task(TASK_TYPE.INITIALIZE, {'turn_number': turn_number})

    @classmethod
    def cmd_next_turn(cls, steps_delta):
        return cls._do_task(TASK_TYPE.NEXT_TURN, {'steps_delta': steps_delta})

    @classmethod
    def cmd_change_person_power(cls, person_id, power_delta):
        return cls._do_task(TASK_TYPE.CHANGE_PERSON_POWER, {'person_id': person_id, 'power_delta': power_delta})




