
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'block expired accounts. MUST run only if game stopped'

    LOCKS = ['game_commands', 'portal_commands']

    GAME_MUST_BE_STOPPED = False

    requires_model_validation = False

    def _handle(self, *args, **options):
        logic.block_expired_accounts(self.logger)
