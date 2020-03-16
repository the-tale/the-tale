
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'create new world'

    LOCKS = ['game_commands', 'portal_commands']

    GAME_MUST_BE_STOPPED = True

    def _handle(self, *args, **options):

        if len(places_storage.places.all()) != 0:
            self.logger.error('world already created')
            return

        logic.create_test_map()

        utils_logic.run_django_command(['map_update_map', '--ignore-lock', 'game_commands'])
