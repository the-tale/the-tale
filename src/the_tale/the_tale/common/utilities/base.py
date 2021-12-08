
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = NotImplemented

    LOCKS = NotImplemented

    SKIP_IF_ALREADY_IN_QUEUE = True
    LOCK_RUNNING_IN_PARALLEL = True

    GAME_MUST_BE_RUNNING = False
    GAME_MUST_BE_STOPPED = False

    GAME_MUST_BE_IN_DEBUG_MODE = False

    GAME_CAN_BE_IN_MAINTENANCE_MODE = False

    def __init__(self, *argv, **kwargs):
        self.logger = self.get_logger()

        self.help += '\n'

        if self.SKIP_IF_ALREADY_IN_QUEUE:
            self.help += '\n - command will be skipped if instance of the same command has already in queue'

        if self.LOCK_RUNNING_IN_PARALLEL:
            self.help += '\n - command does not allow parallel execution'

        if self.GAME_MUST_BE_RUNNING:
            self.help += '\n - command require game to be in RUNNING state'

        if self.GAME_MUST_BE_STOPPED:
            self.help += '\n - command require game to be in STOPPED state'

        if self.GAME_MUST_BE_IN_DEBUG_MODE:
            self.help += '\n - command require game to be in DEBUG mode'

        if self.GAME_CAN_BE_IN_MAINTENANCE_MODE:
            self.help += '\n - command can run when game is in MAINTENANCE mode'

        super().__init__(*argv, **kwargs)

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = argparse.RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--ignore-lock', action='append', dest='ignore_locks', default=[], help='ignore specified lock')
        parser.add_argument('--game-must-be-running',
                            action='store_true',
                            dest='game_must_be_running',
                            default=self.GAME_MUST_BE_RUNNING,
                            help='allow command to run only if game is running')
        parser.add_argument('--game-can-be-stopped',
                            action='store_false',
                            dest='game_must_be_running',
                            default=self.GAME_MUST_BE_RUNNING,
                            help='allow command to run if game is stopped')
        parser.add_argument('--game-can-be-in-maintenance-mode',
                            action='store_true',
                            dest='game_can_be_in_maintenance_mode',
                            default=self.GAME_CAN_BE_IN_MAINTENANCE_MODE,
                            help='allow run command when game in maintenance mode')

    def get_logger(self):
        return logging.getLogger(__name__)

    def handle(self, *args, **options):

        command_name = sys.argv[1]

        if not options['game_can_be_in_maintenance_mode'] and os.path.isfile(django_settings.MAINTENANCE_FILE):
            self.logger.info(f'game is in MAINTENANCE mode, no command can be running')
            return

        record_id = logic.log_command_waiting(name=command_name)

        if options['game_must_be_running'] and game_prototypes.GameState.is_stopped():
            self.logger.info(f'game MUST be running to run command "{command_name}"')
            logic.log_command_finish(record_id, relations.RESULT.GAME_MUST_BE_RUNNING)
            return

        if self.GAME_MUST_BE_STOPPED and game_prototypes.GameState.is_working():
            self.logger.info(f'game MUST be stopped to run command "{command_name}"')
            logic.log_command_finish(record_id, relations.RESULT.GAME_MUST_BE_STOPPED)
            return

        if self.GAME_MUST_BE_IN_DEBUG_MODE and not django_settings.DEBUG:
            self.logger.info(f'game MUST be in debug mode to run command "{command_name}"')
            logic.log_command_finish(record_id, relations.RESULT.GAME_MUST_BE_IN_DEBUG)
            return

        locks_names = list(self.LOCKS)

        if self.LOCK_RUNNING_IN_PARALLEL and command_name not in locks_names:
            locks_names.append(command_name)

        for ignored_lock in options['ignore_locks']:
            if ignored_lock in locks_names:
                self.logger.info(f'ignore lock "{ignored_lock}"')
                locks_names.remove(ignored_lock)

        if self.SKIP_IF_ALREADY_IN_QUEUE and logic.other_command_in_queue(command_name, record_id):
            self.logger.info(f'command "{command_name}" skipped: same command already in queue and waiting')
            logic.log_command_finish(record_id, relations.RESULT.SKIPPED)
            return

        self.logger.info(f'run command "{command_name}"')

        result = relations.RESULT.ERROR

        try:
            with contextlib.ExitStack() as stack:

                for lock_name in locks_names:
                    stack.enter_context(locks_logic.lock(lock_name, logger=self.logger))

                logic.log_command_start(record_id)

                self.logger.info(f'run logic')

                self._handle(*args, **options)

                self.logger.info(f'logic processed')

            result = relations.RESULT.SUCCESS

        finally:
            logic.log_command_finish(record_id, result)

    def _handle(self, *args, **options):
        raise NotImplementedError
