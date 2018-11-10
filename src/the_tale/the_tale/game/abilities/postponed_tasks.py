
import smart_imports

smart_imports.all()


class UseAbilityTask(game_postponed_tasks.ComplexChangeTask):
    TYPE = 'user-ability'

    def construct_processor(self):
        return deck.ABILITIES[relations.ABILITY_TYPE(self.processor_id)]()

    @property
    def processed_data(self):
        return {'message': self.message}
