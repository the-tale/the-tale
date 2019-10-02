
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Kill dead emissaries'

    def handle(self, *args, **options):
        emissaries_logic.damage_emissaries()

        emissaries_logic.kill_dead_emissaries()
