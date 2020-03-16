
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'remove expired acces tokens'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        logic.remove_expired_access_tokens()
