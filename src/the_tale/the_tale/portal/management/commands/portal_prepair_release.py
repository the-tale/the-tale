
import smart_imports

smart_imports.all()


META_CONFIG = django_settings.META_CONFIG


class Command(django_management.BaseCommand):

    help = 'prepair all generated static files'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-g', '--game-version', action='store', type=str, dest='game-version', help='game version')

    def handle(self, *args, **options):

        version = options['game-version']

        if version is None:
            print('game version MUST be specified', file=sys.stderr)
            sys.exit(1)

        print()
        print('GENERATE JAVASCRIPT CONSTANTS')
        print()

        dext_logic.run_django_command(['game_generate_js'])

        print()
        print('GENERATE CSS')
        print()

        dext_logic.run_django_command(['less_generate_css'])

        print()
        print('GENERATE META CONFIG')
        print()

        META_CONFIG.increment_static_data_version()
        META_CONFIG.version = version
        META_CONFIG.save_config()
