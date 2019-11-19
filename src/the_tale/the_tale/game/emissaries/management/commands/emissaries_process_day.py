
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'process everyday operations for emissaries'

    def handle(self, *args, **options):
        emissaries_logic.add_clan_experience()

        emissaries_logic.add_emissaries_experience()

        emissaries_logic.damage_emissaries()

        emissaries_logic.kill_dead_emissaries()
