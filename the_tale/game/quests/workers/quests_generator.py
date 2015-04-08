# coding: utf-8

from the_tale.amqp_environment import environment

from the_tale.common.utils.workers import BaseWorker


class Worker(BaseWorker):
    STOP_SIGNAL_REQUIRED = False
    GET_CMD_TIMEOUT = 60

    def initialize(self):
        pass

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: quests generator already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('QUEST GENERATOR INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        environment.workers.supervisor.cmd_answer('stop', self.worker_id)
        self.logger.info('QUESTS GENERATOR STOPPED')
