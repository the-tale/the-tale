
import smart_imports

smart_imports.all()


class Attributes(game_attributes.create_attributes_class(relations.ATTRIBUTE)):
    __slots__ = ()

    def ability_maximum(self, ability):
        return getattr(self, ('ATTRIBUTE_MAXIMUM__' + ability.name).lower())
