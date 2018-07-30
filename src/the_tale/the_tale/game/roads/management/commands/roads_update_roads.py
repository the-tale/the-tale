
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):

        for road in storage.roads.all():
            road.update()

        storage.roads.save_all()
