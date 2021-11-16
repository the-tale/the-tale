
import smart_imports

smart_imports.all()


DEFAULT_MAINTENANCE = 'on'


class Command(utilities_base.Command):

    help = 'generate css from less sources'

    LOCKS = []

    GAME_CAN_BE_IN_MAINTENANCE_MODE = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--on',
                            action='store_const',
                            const='on',
                            dest='maintenance',
                            default=DEFAULT_MAINTENANCE,
                            help='turn on maintenance mode')

        parser.add_argument('--off',
                            action='store_const',
                            const='off',
                            dest='maintenance',
                            default=DEFAULT_MAINTENANCE,
                            help='turn off maintenance mode')

    def turn_on(self):
        self.logger.info('Turn on maintenance mode.')

        shutil.copy(django_settings.MAINTENANCE_PREDEFINED_FILE,
                    django_settings.MAINTENANCE_FILE)

    def turn_off(self):
        self.logger.info('Turn off maintenance mode.')

        if os.path.exists(django_settings.MAINTENANCE_FILE):
            os.remove(django_settings.MAINTENANCE_FILE)

    def _handle(self, *args, **options):
        if options.get('maintenance', 'on') == 'on':
            self.turn_on()
        else:
            self.turn_off()
