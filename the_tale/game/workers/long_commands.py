# coding: utf-8
import subprocess
import Queue
import time

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker
from the_tale.common import postponed_tasks
from the_tale.common.utils.logic import run_django_command

from the_tale.game.workers.environment import workers_environment as game_environment


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_long_commands')
    name = 'game long commands'
    command_name = 'game_long_commands'
    stop_signal_required = False

    def __init__(self, command_queue, stop_queue):
        super(Worker, self).__init__(command_queue=command_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def run(self):
        while not self.exception_raised and not self.stop_required:
            try:
                self.logger.info('wait for amqp command')
                cmd = self.command_queue.get(block=True, timeout=60)

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to run command')
                settings.refresh()
                self.run_commands()


        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            self.process_cmd(cmd.payload)

    def initialize(self):
        pass

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: long commands already initialized, do reinitialization')

        postponed_tasks.autodiscover()

        self.initialized = True
        self.worker_id = worker_id

        self.logger.info('LONG COMMANDS INITIALIZED')

        game_environment.supervisor.cmd_answer('initialize', self.worker_id)

    def _try_run_command_with_delay(self, cmd, settings_key, delay):
        if time.time() - float(settings.get(settings_key, 0)) > delay:
            settings[settings_key] = str(time.time())
            cmd()
            return True

        return False

    def run_commands(self):
        return


    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        game_environment.supervisor.cmd_answer('stop', self.worker_id)
        self.logger.info('LONG COMMANDS STOPPED')

    def _run_django_subprocess(self, name, cmd):
        self.logger.info('run %s command' % name)
        result = run_django_command(cmd)
        if result:
            self.logger.error('%s ENDED WITH CODE %d' % (name, result))
        else:
            self.logger.info('%s command was processed correctly' % name)

    def _run_system_subprocess(self, name, cmd):
        self.logger.info('run %s command' % name)
        result = subprocess.call(cmd)
        if result:
            self.logger.error('%s ENDED WITH CODE %d' % (name, result))
        else:
            self.logger.info('%s command was processed correctly' % name)

    def run_update_map(self):
        self.logger.info('update map')
        self._run_django_subprocess('update map', ['map_update_map'])
        game_environment.supervisor.cmd_highlevel_data_updated()
        self.logger.info('map updated')


    def cmd_update_map(self):
        return self.send_cmd('update_map')

    def process_update_map(self):
        self.run_update_map()
