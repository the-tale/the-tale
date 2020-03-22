
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Do one emissary calculation step'

    LOCKS = ['game_commands']

    SKIP_IF_ALREADY_IN_QUEUE = False

    def _handle(self, *args, **options):
        emissaries_logic.sync_power()
        emissaries_logic.update_emissaries_ratings()
        emissaries_logic.process_events()
