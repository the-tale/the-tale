
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'give points to clans'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-i', '--interval', action='store', type=int, dest='interval', help='time interval in seconds')

    def handle(self, *args, **options):
        for clan_id in models.Clan.objects.values_list('id', flat=True):
            logic.give_points_for_time(clan_id=clan_id, interval=options['interval'])
