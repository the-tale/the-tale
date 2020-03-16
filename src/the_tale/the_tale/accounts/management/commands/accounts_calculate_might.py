
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Recalculate mights of accounts'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        might.recalculate_accounts_might()
