
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Search orphan effects'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        effects_events = {}

        for effect in places_storage.effects.all():
            if effect.info is None:
                continue

            if 'event' not in effect.info:
                continue

            effects_events[effect.id] = effect.info['event']

        effects_to_remove = set()

        for effect_id, event_id in effects_events.items():
            event = storage.events.get_or_load(event_id)

            if event is None:
                effects_to_remove.add(effect_id)
                self.logger.info(f'effect {effect_id} orphan due event not exists')
                continue

            if event.state.is_STOPPED:
                self.logger.info(f'effect {effect_id} orphan due event is stopped')
                effects_to_remove.add(effect_id)
                continue

            if event.concrete_event.effect_id != effect_id:
                self.logger.info(f'effect {effect_id} orphan due event has other effect')
                effects_to_remove.add(effect_id)
                continue

        self.logger.info(f'all orphan effects: {effects_to_remove}')
