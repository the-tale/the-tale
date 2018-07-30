
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'for each place calculate nearest map cells'

    def handle(self, *args, **options):

        nearest_cells.update_nearest_cells()
