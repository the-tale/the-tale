
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):
        logic.update_waymarks()
