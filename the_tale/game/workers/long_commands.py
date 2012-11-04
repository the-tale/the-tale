# coding: utf-8
import subprocess

from django.conf import settings as project_settings
from django.utils.log import getLogger

from common.amqp_queues import BaseWorker

class TurnsLoopException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, game_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_long_commands'), command_queue=game_queue)


    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def run(self):

        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: logn commands already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('LONG COMMANDS INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('LONG COMMANDS STOPPED')

    def cmd_recalculate_ratings(self):
        return self.send_cmd('recalculate_ratings')

    def process_recalculate_ratings(self):
        subprocess.call(['./manage.py', 'ratings_recalculate_ratings'])

    def cmd_run_vacuum(self):
        return self.send_cmd('recalculate_ratings')

    def process_run_vacuum(self):
        vacuum_result = subprocess.call(['vacuumdb', '-q',
                                         '-U "%s"' % project_settings.DATABASES['default']['USER'],
                                         '-d "%s"' % project_settings.DATABASES['default']['NAME']])
        if vacuum_result:
            self.logger.error('VACUUM COMMAND ENDED WITH CODE %d' % vacuum_result)
