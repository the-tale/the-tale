
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'give points to clans'

    LOCKS = ['game_commands']

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-i', '--interval', action='store', type=int, dest='interval', help='time interval in seconds')

    def _handle(self, *args, **options):
        for clan_id in models.Clan.objects.values_list('id', flat=True):
            logic.give_points_for_time(clan_id=clan_id, interval=options['interval'])
