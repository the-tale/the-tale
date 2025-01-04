import smart_imports

smart_imports.all()


class TYPE(rels_django.DjangoEnum):
    protobuf = rels.Column()

    records = (('REPLACE', 0, 'заменить', tt_protocol_properties_pb2.Property.Mode.REPLACE),
               ('APPEND', 1, 'добавить', tt_protocol_properties_pb2.Property.Mode.APPEND))


class PROPERTIES(rels_django.DjangoEnum):
    to_string = rels.Column(unique=False, single_type=False)
    from_string = rels.Column(unique=False, single_type=False)
    default = rels.Column(unique=False, single_type=False)
    type = rels.Column(unique=False, single_type=True)


def properties_class(properties):
    class PropertiesClass:
        __slots__ = tuple(record.name for record in properties.records)

        def __getattr__(self, name):
            if name not in self.__slots__:
                raise AttributeError('unkown property {}'.format(name))

            default = getattr(properties, name).default

            if callable(default):
                default = default()

            setattr(self, name, default)

            return default

    return PropertiesClass


# code is changed due to moving game to the read-only mode
class Client(client.Client):
    _defaults = {}

    def __init__(self, properties, **kwargs):
        super().__init__(**kwargs)
        self._properties = properties
        self._properties_class = properties_class(properties)
        self._object_defaults = self.load_object_defaults()

    def load_object_defaults(self):
        return None

    def cmd_set_property(self, object_id, name, value):
        raise NotImplementedError("Game in read-only mode")

    def get_property_type_or_raise(self, name):
        if name not in self._properties.records:
            property_type = getattr(self._properties, name, None)
        else:
            property_type = name

        if property_type is None:
            raise exceptions.TTPropertiesError(name=name)

        return property_type

    def cmd_set_properties(self, properties):
        raise NotImplementedError("Game in read-only mode")

    def cmd_get_properties(self, objects):
        properties = {}

        for object_id, names in objects.items():
            properties_types = []

            for name in names:
                property_type = self.get_property_type_or_raise(name)
                properties_types.append(property_type)

            if object_id not in properties:
                properties[object_id] = self._properties_class()

        for property_type in self._properties.records:
            for object_id in objects:
                value = None

                if self._object_defaults is not None and object_id in self._object_defaults:
                    value = self._object_defaults[object_id].get(property_type.value)

                if value is None:
                    value = self._defaults.get(property_type, property_type.default)

                setattr(properties[object_id],
                        property_type.name,
                        value)

        return properties

    def cmd_get_object_property(self, object_id, name):
        properties = self.cmd_get_properties({object_id: [name]})

        if object_id not in properties:
            return getattr(self._properties, name).default

        if name in self._properties.records:
            return getattr(properties[object_id], name.name)
        else:
            return getattr(properties[object_id], name)

    def cmd_get_all_object_properties(self, object_id):
        properties = self.cmd_get_properties({object_id: [property.name for property in self._properties.records]})
        return properties[object_id]

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_properties_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_properties_pb2.DebugClearServiceResponse)
