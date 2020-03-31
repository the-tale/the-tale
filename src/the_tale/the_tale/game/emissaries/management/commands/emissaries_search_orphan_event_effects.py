
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Search orphan effects'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        self.logger.info('search orphan effects')

        effects_events = {}

        for effect in places_storage.effects.all():

            if effect.attribute.type.is_REWRITABLE:
                continue

            if effect.info is None:
                continue

            if 'event' not in effect.info:
                continue

            effects_events[effect.id] = effect.info['event']

        orphan_effects = set()

        for effect_id, event_id in effects_events.items():
            event = storage.events.get_or_load(event_id)

            if event is None:
                orphan_effects.add(effect_id)
                self.logger.info(f'effect {effect_id} orphan due event not exists')
                continue

            if event.state.is_STOPPED:
                self.logger.info(f'effect {effect_id} orphan due event is stopped')
                orphan_effects.add(effect_id)
                continue

            if event.concrete_event.effect_id != effect_id:
                self.logger.info(f'effect {effect_id} orphan due event has other effect')
                orphan_effects.add(effect_id)
                continue

        self.logger.info(f'all orphan effects: {orphan_effects}')

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
