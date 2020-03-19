
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'do one highlevel step'

    LOCKS = ['game_commands']

    SKIP_IF_ALREADY_IN_QUEUE = False
    GAME_MUST_BE_RUNNING = True

    def _handle(self, *args, **options):
        game_logic.highlevel_step(logger=self.logger)

        utils_logic.run_django_command(['map_update_map', '--ignore-lock', 'game_commands'])
