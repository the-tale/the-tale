
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Send notifications about expired premiums'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        prototypes.AccountPrototype.send_premium_expired_notifications()
