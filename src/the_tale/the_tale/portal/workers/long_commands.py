
import smart_imports

smart_imports.all()


from the_tale.portal import signal_processors  # DO NOT REMOVE


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10

    def initialize(self):
        if not conf.settings.ENABLE_WORKER_LONG_COMMANDS:
            return False

        if self.initialized:
            self.logger.warn('WARNING: long commands already initialized, do reinitialization')

        self.initialized = True

        self.logger.info('LONG COMMANDS INITIALIZED')

    def _try_run_command_with_delay(self, cmd, settings_key, delay):
        if time.time() - float(global_settings.get(settings_key, 0)) > delay:
            global_settings[settings_key] = str(time.time())
            cmd()
            return True

        return False

    def process_no_cmd(self):

        # check if new real day started
        if (time.time() - float(global_settings.get(conf.settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY, 0)) > 23.5 * 60 * 60 and
                datetime.datetime.now().hour >= conf.settings.REAL_DAY_STARTED_TIME):
            signals.day_started.send(self.__class__)
            global_settings[conf.settings.SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY] = str(time.time())
            return

        # is cleaning run needed
        if (time.time() - float(global_settings.get(conf.settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY, 0)) > 23.5 * 60 * 60 and
                conf.settings.CLEANING_RUN_TIME <= datetime.datetime.now().hour <= conf.settings.CLEANING_RUN_TIME + 1):
            global_settings[conf.settings.SETTINGS_PREV_CLEANING_RUN_TIME_KEY] = str(time.time())
            self.run_cleaning()
            return

        # is statistics run needed
        if (time.time() - float(global_settings.get(conf.settings.SETTINGS_PREV_STATISTICS_RUN_TIME_KEY, 0)) > 23.5 * 60 * 60 and
                conf.settings.STATISTICS_RUN_TIME <= datetime.datetime.now().hour <= conf.settings.STATISTICS_RUN_TIME + 1):
            global_settings[conf.settings.SETTINGS_PREV_STATISTICS_RUN_TIME_KEY] = str(time.time())
            self.run_statistics()
            return

        # is rating sync needed
        if self._try_run_command_with_delay(cmd=self.run_recalculate_ratings,
                                            settings_key=conf.settings.SETTINGS_PREV_RATINGS_SYNC_TIME_KEY,
                                            delay=conf.settings.RATINGS_SYNC_DELAY):
            return

        # is might sync needed
        if self._try_run_command_with_delay(cmd=self.run_recalculate_might,
                                            settings_key=conf.settings.SETTINGS_PREV_MIGHT_SYNC_TIME_KEY,
                                            delay=conf.settings.MIGHT_SYNC_DELAY):
            return

        # is cdns refresh needed
        if self._try_run_command_with_delay(cmd=self.run_refresh_cdns,
                                            settings_key=conf.settings.SETTINGS_PREV_CDN_SYNC_TIME_KEY,
                                            delay=conf.settings.CDN_SYNC_DELAY):
            return

        # is remove expired access tokens refresh needed
        if self._try_run_command_with_delay(cmd=self.run_remove_expired_access_tokens,
                                            settings_key=conf.settings.SETTINGS_PREV_EXPIRE_ACCESS_TOKENS_SYNC_TIME_KEY,
                                            delay=conf.settings.EXPIRE_ACCESS_TOKENS_SYNC_DELAY):
            return

        # is linguistic cleaning needed
        if self._try_run_command_with_delay(cmd=self.run_clean_removed_templates,
                                            settings_key=conf.settings.SETTINGS_PREV_CLEAN_REMOVED_TEMPLATES_KEY,
                                            delay=conf.settings.EXPIRE_CLEAN_REMOVED_TEMPLATES):
            return

    def _run_django_subprocess(self, name, cmd):
        self.logger.info('run %s command' % name)
        result = utils_logic.run_django_command(cmd)
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

    def run_statistics(self):
        self.logger.info('start statistics')
        self._run_django_subprocess('statistics_complete', ['statistics_complete'])

    def run_remove_expired_access_tokens(self):
        self.logger.info('remove expired access tokens')
        self._run_django_subprocess('third_party_remove_expired_access_tokens', ['third_party_remove_expired_access_tokens'])

    def run_clean_removed_templates(self):
        self.logger.info('clean removed templates')
        self._run_django_subprocess('linguistics_clean_removed_templates', ['linguistics_clean_removed_templates'])

    def run_cleaning(self):
        self.logger.info('start cleaning')
        self._run_django_subprocess('clean', ['portal_clean'])
        self._run_django_subprocess('clearsessions', ['clearsessions'])
        self._run_django_subprocess('personal_messages_remove_system_messages', ['personal_messages_remove_system_messages'])

        self.logger.info('cleaned')
