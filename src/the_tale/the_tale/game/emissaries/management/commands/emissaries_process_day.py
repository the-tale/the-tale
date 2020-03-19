
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'process everyday operations for emissaries'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):
        emissaries_logic.add_clan_experience()

        emissaries_logic.add_emissaries_experience()

        emissaries_logic.damage_emissaries()

        emissaries_logic.kill_dead_emissaries()
