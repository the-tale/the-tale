# coding: utf-8
import sys
import traceback

from django.utils.log import getLogger

from dext.utils.decorators import nested_commit_on_success

from game.prototypes import get_current_time
from game.bundles import get_bundle_by_id, get_bundle_by_model
from game.models import Bundle
from game.abilities.prototypes import AbilityTaskPrototype
from game.heroes.prototypes import ChooseAbilityTaskPrototype
from game.conf import game_settings

logger = getLogger('the-tale.workers.game_supervisor')

class CMD_TYPE:
    NEXT_TURN = 'next_turn'
    REGISTER_BUNDLE = 'register_bundle'
    ACTIVATE_ABILITY = 'activate_ability'
    REGISTER_HERO = 'register_hero'
    CHOOSE_HERO_ABILITY = 'choose_hero_ability'
    STOP = 'stop'

class SupervisorException(Exception): pass


class Worker(object):

    def __init__(self, connection, supervisor_queue, answers_queue, turns_loop_queue, stop_queue):
        self.supervisor_queue = connection.SimpleQueue(supervisor_queue)
        self.answers_queue = connection.SimpleQueue(answers_queue)
        self.turns_loop_queue = connection.SimpleQueue(turns_loop_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)
        self.exception_raised = False
        self.stop_required = False

    def set_turns_loop_worker(self, turns_loop_worker):
        self.turns_loop_worker = turns_loop_worker

    def set_logic_worker(self, logic_worker):
        self.logic_worker = logic_worker

    def set_highlevel_worker(self, highlevel_worker):
        self.highlevel_worker = highlevel_worker

    def close_queries(self):
        # self.supervisor_queue.close()
        # self.answers_queue.close()
        # self.stop_queue.close()
        pass

    def clean_queues(self):
        self.supervisor_queue.queue.purge()
        self.answers_queue.queue.purge()
        self.stop_queue.queue.purge()
        self.turns_loop_queue.queue.purge()

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
        self.logic_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='logic')
        self.wait_answers_from('initialize', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='highlevel')
            self.wait_answers_from('initialize', workers=['highlevel'])

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            self.turns_loop_worker.cmd_initialize(worker_id='turns_loop')
            self.wait_answers_from('initialize', workers=['turns_loop'])

        for bundle_model in Bundle.objects.all():
            bundle = get_bundle_by_model(bundle_model)
            bundle.owner = 'worker'
            bundle.save()
            self.logic_worker.cmd_register_bundle(bundle.id)

        logger.info('SUPERVISOR INITIALIZED')

    def process_game_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        logger.info('<%s> %r' % (cmd_type, cmd_data))

        try:
            { CMD_TYPE.NEXT_TURN: self.process_next_turn,
              CMD_TYPE.REGISTER_BUNDLE: self.process_register_bundle,
              CMD_TYPE.ACTIVATE_ABILITY: self.process_activate_ability,
              CMD_TYPE.REGISTER_HERO: self.process_register_hero,
              CMD_TYPE.CHOOSE_HERO_ABILITY: self.process_choose_hero_ability,
              CMD_TYPE.STOP: self.process_stop}[cmd_type](**cmd_data)
        except Exception, e:
            self.exception_raised = True
            logger.error('EXCEPTION: %s' % e)
            traceback.print_exc()

            logger.error('Game worker exception: game_supervisor',
                         exc_info=sys.exc_info(),
                         extra={} )

    def send_cmd(self, tp, data={}):
        self.supervisor_queue.put({'type': tp, 'data': data}, serializer='json', compression=None)

    def cmd_next_turn(self):
        return self.send_cmd(CMD_TYPE.NEXT_TURN)

    def process_next_turn(self):
        self.time.increment_turn()
        self.time.save()

        self.logic_worker.cmd_next_turn(turn_number=self.time.turn_number)
        self.wait_answers_from('next_turn', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_next_turn(turn_number=self.time.turn_number)
            self.wait_answers_from('next_turn', workers=['highlevel'])

    def cmd_stop(self):
        return self.send_cmd(CMD_TYPE.STOP)

    def process_stop(self):
        self.logic_worker.cmd_stop()
        self.wait_answers_from('stop', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['highlevel'])

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            self.turns_loop_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['turns_loop'])

        self.stop_queue.put({'code': 'stopped', 'worker': 'supervisor'}, serializer='json', compression=None)

        self.stop_required = True

        logger.info('SUPERVISOR STOPPED')


    def cmd_register_bundle(self, bundle_id):
        self.send_cmd(CMD_TYPE.REGISTER_BUNDLE, {'bundle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        with nested_commit_on_success():
            bundle = get_bundle_by_id(bundle_id)
            bundle.owner = 'worker'
            bundle.save()

        self.logic_worker.cmd_register_bundle(bundle_id)

    def cmd_activate_ability(self, ability_task_id):
        self.send_cmd(CMD_TYPE.ACTIVATE_ABILITY, {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        self.logic_worker.cmd_activate_ability(ability_task_id)

    def cmd_register_hero(self, hero_id):
        self.send_cmd(CMD_TYPE.REGISTER_HERO, {'hero_id': hero_id})

    def process_register_hero(self, hero_id):
        self.logic_worker.cmd_register_hero(hero_id)

    def cmd_choose_hero_ability(self, ability_task_id):
        self.send_cmd(CMD_TYPE.CHOOSE_HERO_ABILITY, {'ability_task_id': ability_task_id})

    def process_choose_hero_ability(self, ability_task_id):
        self.logic_worker.cmd_choose_hero_ability(ability_task_id)
