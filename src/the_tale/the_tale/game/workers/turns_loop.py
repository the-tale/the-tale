
import smart_imports

smart_imports.all()


class TurnsLoopException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 0.01
    NO_CMD_TIMEOUT = conf.settings.TURN_DELAY

    def process_no_cmd(self):
        if prototypes.GameState.is_working():
            self.logger.info('send next turn command')
            amqp_environment.environment.workers.supervisor.cmd_next_turn()
        else:
            self.logger.info('skip next turn command, since game is stopped')

    def initialize(self):
        if not conf.settings.ENABLE_WORKER_TURNS_LOOP:
            return False

        if self.initialized:
            self.logger.warn('WARNING: turn loop already initialized, do reinitialization')

        self.initialized = True

        self.logger.info('TURN LOOP INITIALIZED')
