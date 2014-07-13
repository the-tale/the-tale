# coding: utf-8
import subprocess
import Queue
import time
import datetime

from django.conf import settings as project_settings
from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker
from the_tale.common.utils.logic import run_django_command

from the_tale.portal.conf import portal_settings
from the_tale.portal import signals as portal_signals

from the_tale.portal import signal_processors # DO NOT REMOVE


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.portal_long_commands')
    name = 'portal long commands'
    command_name = 'portal_long_commands'

    def __init__(self, command_queue, stop_queue):
        super(Worker, self).__init__(command_queue=command_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def run(self):
        while not self.exception_raised and not self.stop_required:
            try:
                self.logger.info('wait for amqp command')
                cmd = self.command_queue.get(block=True, timeout=60)
                # cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to run command')
                settings.refresh()
                self.run_commands()


        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            # cmd.ack()
            self.process_cmd(cmd.payload)

    def initialize(self):
        if self.initialized:
            self.logger.warn('WARNING: long commands already initialized, do reinitialization')

        self.initialized = True

        self.logger.info('LONG COMMANDS INITIALIZED')

    def _try_run_command_with_delay(self, cmd, settings_key, delay):
        if time.time() - float(settings.get(settings_key, 0)) > delay:
            settings[settings_key] = str(time.time())
            cmd()
            return True

        return False

    def run_commands(self):

        # check if new real day started
        if (time.time() - float(settings.get(portal_settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY, 0)) > 23.5*60*60 and
            datetime.datetime.now().hour >= portal_settings.REAL_DAY_STARTED_TIME):
            portal_signals.day_started.send(self.__class__)
            settings[portal_settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY] = str(time.time())
            return

        # is cleaning run needed
        if (time.time() - float(settings.get(portal_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            portal_settings.CLEANING_RUN_TIME <= datetime.datetime.now().hour <= portal_settings.CLEANING_RUN_TIME + 1):
            settings[portal_settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY] = str(time.time())
            self.run_cleaning()
            return

        # is statistics run needed
        if (time.time() - float(settings.get(portal_settings.SETTINGS_PREV_STATISTICS_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            portal_settings.STATISTICS_RUN_TIME <= datetime.datetime.now().hour <= portal_settings.STATISTICS_RUN_TIME + 1):
            settings[portal_settings.SETTINGS_PREV_STATISTICS_RUN_TIME_KEY] = str(time.time())
            self.run_statistics()
            return

        # is rating sync needed
        if self._try_run_command_with_delay(cmd=self.run_recalculate_ratings,
                                            settings_key=portal_settings.SETTINGS_PREV_RATINGS_SYNC_TIME_KEY,
                                            delay=portal_settings.RATINGS_SYNC_DELAY):
            return

        # is might sync needed
        if self._try_run_command_with_delay(cmd=self.run_recalculate_might,
                                            settings_key=portal_settings.SETTINGS_PREV_MIGHT_SYNC_TIME_KEY,
                                            delay=portal_settings.MIGHT_SYNC_DELAY):
            return

        # is cdns refresh needed
        if self._try_run_command_with_delay(cmd=self.run_refresh_cdns,
                                            settings_key=portal_settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY,
                                            delay=portal_settings.CDN_SYNC_DELAY):
            return

        # is currenciess refresh needed
        if self._try_run_command_with_delay(cmd=self.run_refresh_currencies,
                                            settings_key=portal_settings.SETTINGS_PREV_CURRENCIES_SYNC_TIME_KEY,
                                            delay=portal_settings.CURRENCIES_SYNC_DELAY):
            return


    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'long commands'}, serializer='json', compression=None)
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

    def run_recalculate_ratings(self):
        self.logger.info('calculate ratings')
        self._run_django_subprocess('recalculate_rating', ['ratings_recalculate_ratings'])
        self.logger.info('ratings calculated')

    def run_recalculate_might(self):
        self.logger.info('calculate might')
        self._run_django_subprocess('recalculate_might', ['accounts_calculate_might'])
        self.logger.info('might calculated')

    def run_refresh_cdns(self):
        self.logger.info('refresh cdns')
        self._run_django_subprocess('refresh_cdns', ['portal_refresh_cdns'])
        self.logger.info('cdns refreshed')

    def run_refresh_currencies(self):
        self.logger.info('currencies cdns')
        self._run_django_subprocess('refresh_currencies', ['portal_refresh_currencies'])
        self.logger.info('currencies refreshed')

    def run_statistics(self):
        self.logger.info('start statistics')
        self._run_django_subprocess('statistics', ['statistics_complete'])

    def run_cleaning(self):
        self.logger.info('start cleaning')
        self._run_django_subprocess('clean', ['portal_clean'])
        self._run_django_subprocess('clearsessions', ['clearsessions'])
        self._run_django_subprocess('personal_messages_remove_system_messages', ['personal_messages_remove_system_messages'])

        self.logger.info('cleaned')
