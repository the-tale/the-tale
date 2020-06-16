
import smart_imports

smart_imports.all()


class ATTRIBUTE_TYPE(rels_django.DjangoEnum):
    records = (('AGGREGATED', 0, 'аггрегируемый'),
               ('CALCULATED', 1, 'вычисляемый'),
               ('REWRITABLE', 2, 'перезаписываемый'))


def set_applier(container, value):
    container.add(value)
    return container


def replace_applier(container, value):
    return value


class ATTRIBUTE(rels_django.DjangoEnum):
    default = rels.Column(unique=False, primary=False, single_type=False)
    type = rels.Column(unique=False, primary=False)
    order = rels.Column(unique=False, primary=False)
    description = rels.Column(primary=False)
    apply = rels.Column(primary=False, unique=False, single_type=False)
    verbose_units = rels.Column(unique=False, primary=False)
    serializer = rels.Column(unique=False, single_type=False)
    deserializer = rels.Column(unique=False, single_type=False)
    formatter = rels.Column(unique=False, single_type=False)


def attr(name, value, text, default=lambda: 0, type=ATTRIBUTE_TYPE.AGGREGATED, order=1, description=None, apply=operator.add, verbose_units='', serializer=lambda x: x, deserializer=lambda x: x, formatter=lambda x: x):
    return (name, value, text, default, type, order, (description if description is not None else text), apply, verbose_units, serializer, deserializer, formatter)


def create_attributes_class(ATTRIBUTES):

    class Attributes(object):
        __slots__ = tuple([record.name.lower() for record in ATTRIBUTES.records])

        def __init__(self, **kwargs):
            for name, value in kwargs.items():
                setattr(self, name, value)

            for attribute in ATTRIBUTES.records:
                if not hasattr(self, attribute.name.lower()):
                    setattr(self, attribute.name.lower(), attribute.default())

        def serialize(self):
            return {record.name.lower(): record.serializer(getattr(self, record.name.lower())) for record in ATTRIBUTES.records}

        @classmethod
        def deserialize(cls, data):
            return cls(**{k: getattr(ATTRIBUTES, k.upper()).deserializer(v) for k, v in data.items() if hasattr(ATTRIBUTES, k.upper())})

        def reset(self):
            for attribute in ATTRIBUTES.records:
                if attribute.type.is_CALCULATED:
                    continue
                setattr(self, attribute.name.lower(), attribute.default())

        def attribute_by_name(self, name):
            return getattr(ATTRIBUTES, name)

        def attributes_by_name(self):
            return sorted(ATTRIBUTES.records, key=lambda x: x.text)

        def effects_order(self):
            return ATTRIBUTES.EFFECTS_ORDER

        def sync(self):
            pass

        def __eq__(self, other):
            return self.serialize() == other.serialize()

        def __ne__(self, other):
            return not self.__eq__(other)

    return Attributes


def attributes_info(effects, attrs, relation):
    attributes = []

    for record in relation.records:
        value = getattr(attrs, record.name.lower())
        if not isinstance(value, (numbers.Number, str)):
            value = None
        attributes.append({"id": record.value, "value": value})

    return {'effects': [effect.ui_info() for effect in effects],
            'attributes': attributes}


def percents_formatter(value):
    return '%.2f' % round(value * 100, 2)


def float_formatter(value):
    return '%.2f' % round(value, 2)


def clan_formatter(value):
    from the_tale.clans import storage as clans_storage

    if value is None:
        return '—'

    clan = clans_storage.infos[value]

    return f'[{clan.abbr}] {clan.name}'


class AttributesMixin:

    def effects_generator(self, order):
        for effect in self._effects_generator():
            if effect.attribute.order != order:
                continue
            yield effect

    def effects_for_attribute(self, attribute):
        for effect in self.effects_generator(attribute.order):
            if effect.attribute == attribute:
                yield effect

    def tooltip_effects_for_attribute(self, attribute):
        effects = [(effect.name, effect.value) for effect in self.effects_for_attribute(attribute)]
        effects.sort(key=lambda x: x[1], reverse=True)
        return effects

    def attribute_ui_info(self, attribute_name):
        attribute = self.attrs.attribute_by_name(attribute_name.upper())
        return (attribute, getattr(self.attrs, attribute_name.lower()))

    def all_effects(self):
        for order in self.attrs.effects_order():
            for effect in self.effects_generator(order):
                yield effect

    def refresh_attributes(self):
        self.attrs.reset()

        for effect in self.all_effects():
            effect.apply_to(self.attrs)

        self.attrs.sync()
