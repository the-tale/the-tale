
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Reset free quests amount for clans'

    def handle(self, *args, **options):
        for clan_id in models.Clan.objects.values_list('id', flat=True):
            logic.reset_free_quests(clan_id=clan_id)
