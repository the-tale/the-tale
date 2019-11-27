
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Do one emissary monitoring action'

    def handle(self, *args, **options):
        emissaries_logic.process_events_monitoring()
