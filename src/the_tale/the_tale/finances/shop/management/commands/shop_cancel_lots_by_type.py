
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'cancel all market lots of specified item type'

    LOCKS = ['portal_commands']

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-t', '--type', action='store', type=str, dest='type', help='item type')

    def _handle(self, *args, **options):

        lots = logic.cancel_lots_by_type(item_type=options['type'])

        self.logger.info(f'lots canceled: {len(lots)}')
