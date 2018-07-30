
import smart_imports

smart_imports.all()


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
        if time.time() - float(dext_settings.settings.get(settings_key, 0)) > delay:
            dext_settings.settings[settings_key] = str(time.time())
            cmd()
            return True

        return False

    def _run_django_subprocess(self, name, cmd):
        self.logger.info('run %s command' % name)
        result = dext_logic.run_django_command(cmd)
        if result:
            self.logger.error('%s ENDED WITH CODE %d' % (name, result))
        else:
            self.logger.info('%s command was processed correctly' % name)

    def run_update_map(self):
        self.logger.info('update map')
        self._run_django_subprocess('update map', ['map_update_map'])
        amqp_environment.environment.workers.supervisor.cmd_highlevel_data_updated()
        self.logger.info('map updated')

    def cmd_update_map(self):
        return self.send_cmd('update_map')

    def process_update_map(self):
        self.run_update_map()
