import smart_imports

smart_imports.all()


logger = logging.getLogger('the-tale.workers.game_highlevel')


class Command(django_management.BaseCommand):

    help = 'update map on base of current database state'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-n',
                            '--number',
                            action='store',
                            type=int,
                            dest='repeate_number',
                            default=1,
                            help='howe many times do generation')

    def handle(self, *args, **options):

        try:
            for i in range(options['repeate_number']):
                generator.update_map(index=storage.map_info.item.id + 1)
        except Exception:
            traceback.print_exc()
            logger.error('Map generation exception',
                         exc_info=sys.exc_info(),
                         extra={})
