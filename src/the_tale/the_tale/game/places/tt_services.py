
import smart_imports

smart_imports.all()


class EffectsClient(tt_api_effects.Client):
    pass


effects = EffectsClient(entry_point=conf.settings.TT_PLACES_EFFECTS_ENTRY_POINT,
                        attribute_relation=relations.ATTRIBUTE)
