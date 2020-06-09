
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Do one emissary monitoring action'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):
        emissaries_logic.emissaries_monitoring()
        emissaries_logic.process_events_monitoring()
