import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'update map on base of current database state'

    LOCKS = ['game_commands']

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-n',
                            '--number',
                            action='store',
                            type=int,
                            dest='repeate_number',
                            default=1,
                            help='howe many times do generation')

    def _handle(self, *args, **options):

        for i in range(options['repeate_number']):
            generator.update_map(index=storage.map_info.item.id + 1)
