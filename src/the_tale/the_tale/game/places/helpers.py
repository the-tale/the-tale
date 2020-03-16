
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

    def set_protector(self, place_id, clan_id):
        logic.register_effect(place_id=place_id,
                              attribute=relations.ATTRIBUTE.CLAN_PROTECTOR,
                              value=clan_id,
                              name='test',
                              refresh_effects=True,
                              refresh_places=True,
                              info={})
