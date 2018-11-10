
import smart_imports

smart_imports.all()


class UseAbilityTaskMixin(game_helpers.ComplexChangeTaskMixin):
    LOGIC = postponed_tasks.UseAbilityTask
