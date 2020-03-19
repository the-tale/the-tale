
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Remove most of users from database, reatain only specified amount + all clan, forumm, folclor users. Also actualize their active states.'

    LOCKS = ['game_commands', 'portal_commands']

    GAME_MUST_BE_STOPPED = True
    GAME_MUST_BE_IN_DEBUG_MODE = True

    requires_model_validation = False

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-n', '--number',
                            action='store',
                            type=int,
                            dest='accounts_number',
                            default=1000,
                            help='howe many accounts muse be remained')

    def _handle(self, *args, **options):
        logic.thin_out_accounts(options['accounts_number'], 30 * 24 * 60 * 60, logger=self.logger)
