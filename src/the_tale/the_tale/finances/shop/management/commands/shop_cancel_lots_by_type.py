
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'cancel all market lots of specified item type'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-t', '--type', action='store', type=str, dest='type', help='item type')

    def handle(self, *args, **options):

        lots = logic.cancel_lots_by_type(item_type=options['type'])

        print('lots canceled: ', len(lots))
