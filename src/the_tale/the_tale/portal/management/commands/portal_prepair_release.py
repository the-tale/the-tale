
import smart_imports

smart_imports.all()


META_CONFIG = django_settings.META_CONFIG


class Command(utilities_base.Command):

    help = 'prepair all generated static files'

    LOCKS = ['portal_commands']

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-g', '--game-version', action='store', type=str, dest='game-version', help='game version')

    def _handle(self, *args, **options):

        version = options['game-version']

        if version is None:
            self.logger.info('game version MUST be specified')
            sys.exit(1)

        self.logger.info('')
        self.logger.info('GENERATE JAVASCRIPT CONSTANTS')
        self.logger.info('')

        utils_logic.run_django_command(['game_generate_js', '--ignore-lock', 'portal_commands'])

        self.logger.info('')
        self.logger.info('GENERATE CSS')
        self.logger.info('')

        utils_logic.run_django_command(['less_generate_css', '--ignore-lock', 'portal_commands'])

        self.logger.info('')
        self.logger.info('GENERATE META CONFIG')
        self.logger.info('')

        META_CONFIG.increment_static_data_version()
        META_CONFIG.version = version
        META_CONFIG.save_config()
