
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'create new world'

    def handle(self, *args, **options):
        if len(places_storage.places.all()) != 0:
            return

        logic.create_test_map()

        dext_logic.run_django_command(['map_update_map'])
