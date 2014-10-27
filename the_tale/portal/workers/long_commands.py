# coding: utf-8
import subprocess
import time
import datetime

from dext.settings import settings

from the_tale.common.utils.workers import BaseWorker
from dext.common.utils.logic import run_django_command

from the_tale.portal.conf import portal_settings
from the_tale.portal import signals as portal_signals

from the_tale.portal import signal_processors # DO NOT REMOVE


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 60

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

    def process_no_cmd(self):

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

        # is backup run needed
        if (time.time() - float(settings.get(portal_settings.SETTINGS_PREV_BACKUP_RUN_TIME_KEY, 0)) > 23.5*60*60 and
            portal_settings.BACKUP_RUN_TIME <= datetime.datetime.now().hour <= portal_settings.BACKUP_RUN_TIME + 1):
            settings[portal_settings.SETTINGS_PREV_BACKUP_RUN_TIME_KEY] = str(time.time())
            self.run_backup()
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

        # is remove expired access tokens refresh needed
        if self._try_run_command_with_delay(cmd=self.run_remove_expired_access_tokens,
                                            settings_key=portal_settings.SETTINGS_PREV_EXPIRE_ACCESS_TOKENS_SYNC_TIME_KEY,
                                            delay=portal_settings.EXPIRE_ACCESS_TOKENS_SYNC_DELAY):
            return




    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'portal long commands'}, serializer='json', compression=None)
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
        self._run_django_subprocess('statistics_complete', ['statistics_complete'])

    def run_remove_expired_access_tokens(self):
        self.logger.info('remove expired access tokens')
        self._run_django_subprocess('third_party_remove_expired_access_tokens', ['third_party_remove_expired_access_tokens'])

    def run_backup(self):
        self.logger.info('start backup')
        self._run_django_subprocess('backup', ['portal_dump'])

    def run_cleaning(self):
        self.logger.info('start cleaning')
        self._run_django_subprocess('clean', ['portal_clean'])
        self._run_django_subprocess('clearsessions', ['clearsessions'])
        self._run_django_subprocess('personal_messages_remove_system_messages', ['personal_messages_remove_system_messages'])

        self.logger.info('cleaned')
