
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'do new day actions'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        logic.new_day_actions()
