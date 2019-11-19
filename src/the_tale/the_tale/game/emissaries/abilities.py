
import smart_imports

smart_imports.all()


class Abilities:
    __slots__ = ('_abilities', )

    def __init__(self, abilities=None):
        if abilities is None:
            abilities = {}

        self._abilities = abilities

    def serialize(self):
        abilities = {ability.value: value
                     for ability, value in self._abilities.items()}

        return {'abilities': abilities}

    @classmethod
    def deserialize(cls, data):
        abilities = {relations.ABILITY(int(ability_id)): value
                     for ability_id, value in data['abilities'].items()}
        return cls(abilities=abilities)

    def items(self):
        for ability in relations.ABILITY.records:
            yield ability, self._abilities.get(ability, 0)

    def grow(self, attributes, abilities):
        for ability in abilities:
            experience = getattr(attributes, ('ATTRIBUTE_GROW_SPEED__{}'.format(ability.name)).lower())

            self[ability] += experience
            self[ability] = min(self[ability], getattr(attributes, ('ATTRIBUTE_MAXIMUM__{}'.format(ability.name)).lower()))

    def total_level(self):
        return sum(self._abilities.values())

    def __getitem__(self, ability):
        if ability not in relations.ABILITY.records:
            raise KeyError(ability)

        return self._abilities.get(ability, 0)

    def __setitem__(self, ability, value):
        if ability not in relations.ABILITY.records:
            raise KeyError(ability)

        self._abilities[ability] = value

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, field) == getattr(other, field) for field in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
