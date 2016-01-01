# coding: utf-8

from . import relations


class Effect(object):
    __slots__ = ('name', 'attribute', 'value', 'delta', 'remove_required')

    def __init__(self, name, attribute, value, delta=None):
        self.name = name
        self.attribute = attribute
        self.value = value
        self.delta = delta
        self.remove_required = False


    def serialize(self):
        return {'name': self.name,
                'attribute': self.attribute.value,
                'value': self.value,
                'delta': self.delta}

    @classmethod
    def deserialize(cls, data):
        return cls(name=data.pop('name'),
                   attribute=relations.ATTRIBUTE(data.pop('attribute')),
                   value=data.pop('value'),
                   delta=data.pop('delta'))

    def info(self):
        return {'name': self.name,
                'attribute': self.attribute.name.lower(),
                'value': self.value}

    def apply_to(self, place):
        name = self.attribute.name.lower()
        setattr(place.attrs, name, getattr(place.attrs, name) + self.value)

    def step(self, delta=None):
        if delta is None:
            delta = self.delta

        old_value = self.value

        if self.value > 0:
            self.value -= delta
        else:
            self.value += delta

        if old_value * self.value <= 0:
            self.remove_required = True


class Container(object):
    __slots__ = ('effects', )

    def __init__(self, effects=None):
        self.effects = effects if effects is not None else []

    def serialize(self):
        return {'effects': [effect.serialize() for effect in self.effects]}

    @classmethod
    def deserialize(cls, data):
        if data is None:
            return cls()

        effects = [Effect.deserialize(effect_data) for effect_data in data['effects']]
        return cls(effects=effects)

    def add(self, effect):
        self.effects.append(effect)

    def update_step(self, place):
        stability_effects = [effect for effect in self.effects if effect.attribute.is_STABILITY]
        if stability_effects:
            stability_delta = place.attrs.stability_renewing_speed / len(stability_effects)

            for effect in stability_effects:
                effect.step(delta=stability_delta)

        for effect in self.effects:
            if effect.attribute.is_STABILITY:
                continue
            effect.step()

        self.effects = [effect for effect in self.effects if not effect.remove_required]
