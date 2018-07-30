
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'update map on base of current database state'

    def handle(self, *args, **options):
        dext_logic.run_django_command(['roads_update_roads'])

        dext_logic.run_django_command(['roads_update_waymarks'])

        dext_logic.run_django_command(['places_update_nearest_cells'])

        dext_logic.run_django_command(['map_generate_map'])
