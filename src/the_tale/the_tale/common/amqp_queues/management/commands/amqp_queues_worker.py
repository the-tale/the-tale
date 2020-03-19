
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'run specified workers'

    LOCKS = []
    SKIP_IF_ALREADY_IN_QUEUE = False
    LOCK_RUNNING_IN_PARALLEL = False
    GAME_CAN_BE_IN_MAINTENANCE_MODE = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-w', '--worker', action='store', type=str, dest='worker', help='worker name')

    requires_model_validation = False

    def _handle(self, *args, **options):

        worker_name = options['worker']

        env = environment.get_environment()

        worker = env.workers.get_by_name(worker_name)

        if worker is None:
            raise Exception('Worker {name} has not found'.format(name=worker_name))

        self._handle_worker(worker)

    def _handle_worker(self, worker):
        try:
            signal.signal(signal.SIGTERM, worker.on_sigterm)

            if worker.initialize() is False:
                worker.logger.info('worker stopped due method initilize return False')
                return

            worker.run()

            worker.logger.info('worker stopped')

        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            if worker and worker.logger:
                worker.logger.error('Infrastructure worker exception: %s' % worker.name,
                                    exc_info=sys.exc_info(),
                                    extra={})
            raise

        # TODO: close worker's queues
