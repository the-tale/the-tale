# coding: utf-8
import subprocess
import Queue
import time
import datetime

from django.conf import settings as project_settings
from django.utils.log import getLogger

from dext.settings import settings

from common.amqp_queues import connection, BaseWorker

from portal.conf import portal_settings


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.portal_long_commands')
    name = 'game long commands'
    command_name = 'portal_long_commands'

    def __init__(self, command_queue, stop_queue):
        super(Worker, self).__init__(command_queue=command_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def run(self):
        while not self.exception_raised and not self.stop_required:
            try:
                self.logger.info('wait for amqp command')
                cmd = self.command_queue.get(block=True, timeout=60)
                cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to run command')
                settings.refresh()
                self.run_commands()


        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

    def initialize(self):
        if self.initialized:
            self.logger.warn('WARNING: long commands already initialized, do reinitialization')

        self.initialized = True

        self.logger.info('LONG COMMANDS INITIALIZED')

    def run_commands(self):

        # is cleaning run needed
        if (time.time() - float(settings.get(portal_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            portal_settings.CLEANING_RUN_TIME <= datetime.datetime.now().hour <= portal_settings.CLEANING_RUN_TIME + 1):
            settings[portal_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY] = str(time.time())
            self.run_cleaning()
            return

        # is rating sync needed
        if time.time() - float(settings.get(portal_settings.SETTINGS_PREV_RATINGS_SYNC_TIME_KEY, 0)) > portal_settings.RATINGS_SYNC_DELAY:
            settings[portal_settings.SETTINGS_PREV_RATINGS_SYNC_TIME_KEY] = str(time.time())
            self.run_recalculate_ratings()
            return

        # is might sync needed
        if time.time() - float(settings.get(portal_settings.SETTINGS_PREV_MIGHT_SYNC_TIME_KEY, 0)) > portal_settings.MIGHT_SYNC_DELAY:
            settings[portal_settings.SETTINGS_PREV_MIGHT_SYNC_TIME_KEY] = str(time.time())
            self.run_recalculate_might()
            return

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'long commands'}, serializer='json', compression=None)
        self.logger.info('LONG COMMANDS STOPPED')

    def _run_subprocess(self, name, cmd):
        self.logger.info('run %s command' % name)
        result = subprocess.call(cmd)
        if result:
            self.logger.error('%s ENDED WITH CODE %d' % (name, result))
        else:
            self.logger.info('%s command was processed correctly' % name)

    def run_recalculate_ratings(self):
        self.logger.info('calculate ratings')
        self._run_subprocess('recalculate_rating', ['./manage.py', 'ratings_recalculate_ratings'])
        self.logger.info('ratings calculated')

    def run_recalculate_might(self):
        self.logger.info('calculate might')
        self._run_subprocess('recalculate_might', ['./manage.py', 'accounts_calculate_might'])
        self.logger.info('might calculated')

    def run_cleaning(self):
        self.logger.info('start cleaning')
        self._run_subprocess('clean', ['./manage.py', 'portal_clean'])
        self._run_subprocess('clearsessions', ['./manage.py', 'clearsessions'])
        self._run_subprocess('vacuumdb', ['vacuumdb', '-q',
                                         '-U', project_settings.DATABASES['default']['USER'],
                                         '-d', project_settings.DATABASES['default']['NAME']])

        self.logger.info('cleaned')
