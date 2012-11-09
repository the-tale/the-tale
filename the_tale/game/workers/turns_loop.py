# coding: utf-8
import time
import Queue

from django.utils.log import getLogger

from common.amqp_queues import BaseWorker

from game.conf import game_settings

class TurnsLoopException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, game_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_turns_loop'), command_queue=game_queue)


    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('send next turn command')
                self.supervisor_worker.cmd_next_turn()
                time.sleep(game_settings.TURN_DELAY)

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: turn loop already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('TURN LOOP INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('TURN LOOP STOPPED')
