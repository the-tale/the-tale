# coding: utf-8

from the_tale.amqp_environment import environment

from the_tale.common.utils.workers import BaseWorker

from the_tale.game.conf import game_settings
from the_tale.game.prototypes import GameState


class TurnsLoopException(Exception): pass

class Worker(BaseWorker):
    STOP_SIGNAL_REQUIRED = False
    GET_CMD_TIMEOUT = 0
    NO_CMD_TIMEOUT = game_settings.TURN_DELAY

    def process_no_cmd(self):
        if GameState.is_working():
            self.logger.info('send next turn command')
            environment.workers.supervisor.cmd_next_turn()

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

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        environment.workers.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('TURN LOOP STOPPED')
