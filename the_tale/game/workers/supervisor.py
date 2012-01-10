# coding: utf-8
import traceback

from django_next.utils.decorators import nested_commit_on_success

from ..prototypes import get_current_time
from ..bundles import get_bundle_by_id, get_bundle_by_model
from ..models import Bundle
from ..abilities.prototypes import AbilityTaskPrototype
from ..heroes.prototypes import ChooseAbilityTaskPrototype


class CMD_TYPE:
    NEXT_TURN = 'next_turn'
    REGISTER_BUNDLE = 'register_bundle'
    ACTIVATE_ABILITY = 'activate_ability'
    REGISTER_HERO = 'register_hero'
    CHOOSE_HERO_ABILITY = 'choose_hero_ability'

class SupervisorException(Exception): pass


class Worker(object):

    def __init__(self, connection, supervisor_queue, answers_queue):
        self.supervisor_queue = connection.SimpleQueue(supervisor_queue)
        self.answers_queue = connection.SimpleQueue(answers_queue)
        self.exception_raised = False
        self.stop_required = False
        print 'SUPERVISOR CONSTRUCTED'

    def set_game_worker(self, game_worker):
        self.game_worker = game_worker

    def set_highlevel_worker(self, highlevel_worker):
        self.highlevel_worker = highlevel_worker

    def close_queries(self):
        self.supervisor_queue.close()
        self.answers_queue.close()

    def clean_queues(self):
        self.supervisor_queue.queue.purge()
        self.answers_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            game_cmd = self.supervisor_queue.get(block=True)
            game_cmd.ack()
            self.process_game_cmd(game_cmd.payload)


    def wait_answers_from(self, code, workers=[]):
        
        while workers:

            answer_cmd = self.answers_queue.get(block=True)
            answer_cmd.ack()

            cmd = answer_cmd.payload

            if cmd['code'] == code:
                worker_id = cmd['worker']
                if worker_id in workers:
                    workers.remove(worker_id)
                else:
                    raise SupervisorException('unexpected unswer from worker: %r' % cmd)
            else:
                raise SupervisorException('wrong answer: %r, expected answers from %r' % (cmd, workers))

    def cmd_answer(self, code, worker):
        self.answers_queue.put({'code': code, 'worker': worker}, serializer='json', compression=None)

    def initialize(self):
        self.time = get_current_time()

        #clearing
        AbilityTaskPrototype.reset_all()
        ChooseAbilityTaskPrototype.reset_all()

        #initialization
        self.game_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='game')
        self.highlevel_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='highlevel')
        self.wait_answers_from('initialize', workers=['game', 'highlevel'])

        for bundle_model in Bundle.objects.all():
            bundle = get_bundle_by_model(bundle_model)
            bundle.owner = 'worker'
            bundle.save()
            self.game_worker.cmd_register_bundle(bundle.id)

        print 'SUPERVISOR INITIALIZED'

    def process_game_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        print '<%s> %r' % (cmd_type, cmd_data)

        try:
            { CMD_TYPE.NEXT_TURN: self.process_next_turn,
              CMD_TYPE.REGISTER_BUNDLE: self.process_register_bundle,
              CMD_TYPE.ACTIVATE_ABILITY: self.process_activate_ability,
              CMD_TYPE.REGISTER_HERO: self.process_register_hero,
              CMD_TYPE.CHOOSE_HERO_ABILITY: self.process_choose_hero_ability}[cmd_type](**cmd_data)
        except Exception, e:
            self.exception_raised = True
            print 'EXCEPTION: %s' % e
            traceback.print_exc()

    def send_cmd(self, tp, data={}):
        self.supervisor_queue.put({'type': tp, 'data': data}, serializer='json', compression=None)

    def cmd_next_turn(self):
        return self.send_cmd(CMD_TYPE.NEXT_TURN)

    def process_next_turn(self):
        self.time.increment_turn()
        self.time.save()

        self.game_worker.cmd_next_turn(turn_number=self.time.turn_number)
        self.wait_answers_from('next_turn', workers=['game'])

        self.highlevel_worker.cmd_next_turn(turn_number=self.time.turn_number)
        self.wait_answers_from('next_turn', workers=['highlevel'])


    def cmd_register_bundle(self, bundle_id):
        self.send_cmd(CMD_TYPE.REGISTER_BUNDLE, {'budle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        with nested_commit_on_success():
            bundle = get_bundle_by_id(bundle_id)
            bundle.owner = 'worker'
            bundle.save()

        self.game_worker.cmd_register_bundle(bundle_id)

    def cmd_activate_ability(self, ability_task_id):
        self.send_cmd(CMD_TYPE.ACTIVATE_ABILITY, {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        self.game_worker.cmd_activate_ability(ability_task_id)

    def cmd_register_hero(self, hero_id):
        self.send_cmd(CMD_TYPE.REGISTER_HERO, {'hero_id': hero_id})

    def process_register_hero(self, hero_id):
        self.game_worker.cmd_register_hero(hero_id)

    def cmd_choose_hero_ability(self, ability_task_id):
        self.send_cmd(CMD_TYPE.CHOOSE_HERO_ABILITY, {'ability_task_id': ability_task_id})

    def process_choose_hero_ability(self, ability_task_id):
        self.game_worker.cmd_choose_hero_ability(ability_task_id)
