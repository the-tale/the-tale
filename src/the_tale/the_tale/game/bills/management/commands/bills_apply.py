
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'apply ready bills'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        if logic.apply_bills(logger=self.logger):
            utils_logic.run_django_command(['map_update_map', '--ignore-lock', 'game_commands'])
