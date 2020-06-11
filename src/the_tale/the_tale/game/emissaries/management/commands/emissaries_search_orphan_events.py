
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Search orphan effects'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        self.logger.info('search orphan events')

        orphan_events = set()

        for event in storage.events.all():

            if not event.state.is_RUNNING:
                continue

            effect_id = getattr(event.concrete_event, 'effect_id', None)

            if effect_id is None:
                continue

            if effect_id in places_storage.effects:
                continue

            orphan_events.add(event.id)

        self.logger.info(f'all orphan events: {orphan_events}')
