
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Search orphan effects'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        self.logger.info('remove orphan effects')

        logic.remove_orphan_event_effects(logger=self.logger)
