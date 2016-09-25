# coding: utf-8
import numbers

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
    def deserialize(cls, data, ATTRIBUTES_RELATION):
        return cls(name=data.pop('name'),
                   attribute=ATTRIBUTES_RELATION(data.pop('attribute')),
                   value=data.pop('value'),
                   delta=data.pop('delta'))

    def ui_info(self):
        return {'name': self.name,
                'attribute': self.attribute.value,
                'value': self.value if isinstance(self.value, (numbers.Number, basestring)) else None}

    def apply_to(self, attrs):
        name = self.attribute.name.lower()
        setattr(attrs, name, self.attribute.apply(getattr(attrs, name), self.value))

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


def create_container(ATTRIBUTES_RELATION):

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

            effects = [Effect.deserialize(effect_data, ATTRIBUTES_RELATION) for effect_data in data['effects']]
            return cls(effects=effects)

        def add(self, effect):
            self.effects.append(effect)

        def update_step(self, deltas):
            for effect in self.effects:
                effect.step(delta=deltas.get(effect.attribute))

            self.effects = [effect for effect in self.effects if not effect.remove_required]

    return Container
