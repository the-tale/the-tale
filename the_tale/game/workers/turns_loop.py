# coding: utf-8
import time
import Queue

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import BaseWorker

from the_tale.game.conf import game_settings
from the_tale.game.workers.environment import workers_environment as game_environment
from the_tale.game.prototypes import GameState


class TurnsLoopException(Exception): pass

class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_turns_loop')
    name = 'game turns loop'
    command_name = 'game_turns_loop'
    stop_signal_required = False

    def __init__(self, game_queue):
        super(Worker, self).__init__(command_queue=game_queue)

    def run(self):

        while not self.exception_raised and not self.stop_required:
            settings.refresh()
            try:
                cmd = self.command_queue.get_nowait()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                if GameState.is_working():
                    self.logger.info('send next turn command')
                    game_environment.supervisor.cmd_next_turn()
                time.sleep(game_settings.TURN_DELAY)

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: turn loop already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('TURN LOOP INITIALIZED')

        game_environment.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        game_environment.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('TURN LOOP STOPPED')
