
import smart_imports

smart_imports.all()


class PlacesTestsMixin:

    def create_effect(self, place_id, value, attribute, delta=None):
        effect = tt_api_effects.Effect(id=None,
                                       attribute=attribute,
                                       entity=place_id,
                                       value=value,
                                       name='test',
                                       delta=delta)
        tt_services.effects.cmd_register(effect)
        storage.effects.refresh()
