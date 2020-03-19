
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'monitor protectorates'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):
        logic.monitor_protectorates()
