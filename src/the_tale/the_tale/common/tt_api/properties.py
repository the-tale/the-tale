import smart_imports

smart_imports.all()


class PROPERTIES(rels_django.DjangoEnum):
    to_string = rels.Column(unique=False, single_type=False)
    from_string = rels.Column(unique=False, single_type=False)
    default = rels.Column(unique=False, single_type=False)


def properties_class(properties):
    class PropertiesClass:
        __slots__ = tuple(record.name for record in properties.records)

        def __getattr__(self, name):
            if name in self.__slots__:
                return getattr(properties, name).default

            raise AttributeError('unkown property {}'.format(name))

    return PropertiesClass


class Client(client.Client):

    PROPERTIES = NotImplemented

    def __init__(self, properties, **kwargs):
        super().__init__(**kwargs)
        self._properties = properties
        self._properties_class = properties_class(properties)

    def cmd_set_property(self, object_id, name, value):
        return self.cmd_set_properties([(object_id, name, value)])

    def cmd_set_properties(self, properties):
        pb_properties = []

        for object_id, name, value in properties:
            property_type = getattr(self._properties, name, None)

            if property_type is None:
                raise exceptions.TTPropertiesError(name=name)

            pb_properties.append(tt_protocol_properties_pb2.Property(object_id=object_id,
                                                                     type=property_type.value,
                                                                     value=property_type.to_string(value)))

        operations.sync_request(url=self.url('set-properties'),
                                data=tt_protocol_properties_pb2.SetPropertiesRequest(properties=pb_properties),
                                AnswerType=tt_protocol_properties_pb2.SetPropertiesResponse)

    def cmd_get_properties(self, objects):

        requests = []

        properties = {}

        for object_id, names in objects.items():
            for name in names:
                if not hasattr(self._properties, name):
                    raise exceptions.TTPropertiesError(name=name)

            if object_id not in properties:
                properties[object_id] = self._properties_class()

            requests.append(tt_protocol_properties_pb2.PropertiesList(object_id=object_id,
                                                                      types=[getattr(self._properties, name).value
                                                                             for name in names]))

        answer = operations.sync_request(url=self.url('get-properties'),
                                         data=tt_protocol_properties_pb2.GetPropertiesRequest(objects=requests),
                                         AnswerType=tt_protocol_properties_pb2.GetPropertiesResponse)

        for property in answer.properties:
            property_type = self._properties(property.type)

            setattr(properties[property.object_id],
                    property_type.name,
                    property_type.from_string(property.value))

        return properties

    def cmd_get_object_property(self, object_id, name):
        properties = self.cmd_get_properties({object_id: [name]})

        if object_id not in properties:
            return getattr(self._properties, name).default

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
