# coding: utf-8
import time
import Queue

from django.utils.log import getLogger

from common.amqp_queues import BaseWorker

from game.conf import game_settings

from game.angels.prototypes import AngelPrototype
from game.angels.models import Angel

class MightCalculatorException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, game_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_might_calculator'), command_queue=game_queue)


    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.update_one_angel()
                time.sleep(game_settings.MIGHT_CALCULATOR_DELAY)

    def update_one_angel(self):
        try:
            # TODO: filter by "active" state
            angel = AngelPrototype(Angel.objects.filter(account__is_fast=False).order_by('might_updated_time')[0])
        except IndexError:
            return
        self.logger.info('calculate might of angel %d' % angel.id)
        self.supervisor_worker.cmd_set_might(angel.id, angel.calculate_might())


    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: might calculation loop already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('MIGHT CALCULATOR INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save bundles, since they automaticaly saved on every turn
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('MIGHT CALCULATOR STOPPED')
