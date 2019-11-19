import smart_imports

smart_imports.all()


class Effect:
    __slots__ = ('id', 'attribute', 'entity', 'value', 'name', 'delta', 'info')

    def __init__(self, id, attribute, entity, value, name, delta=None, info=None):
        self.id = id
        self.attribute = attribute
        self.entity = entity
        self.value = value
        self.name = name
        self.delta = delta
        self.info = info

    def apply_to(self, attrs):
        name = self.attribute.name.lower()
        setattr(attrs, name, self.attribute.apply(getattr(attrs, name), self.value))

    def require_updating(self):
        return self.delta is not None

    def step(self):

        old_value = self.value

        if self.value > 0:
            self.value -= self.delta
        else:
            self.value += self.delta

        if old_value * self.value <= 0:
            return False

        return True

    def ui_info(self):
        return {'name': self.name,
                'attribute': self.attribute.value,
                'value': self.value}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, field) == getattr(other, field) for field in self.__class__.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)


class Client(client.Client):
    __slots__ = ('attribute_relation',)

    def __init__(self, attribute_relation, **kwargs):
        super().__init__(**kwargs)
        self.attribute_relation = attribute_relation

    def protobuf_from_effect(self, effect):
        return tt_protocol_effects_pb2.Effect(id=effect.id,
                                              attribute=effect.attribute.value,
                                              entity=effect.entity,
                                              value=s11n.to_json(effect.value),
                                              caption=effect.name,
                                              data=s11n.to_json({'delta': effect.delta,
                                                                 'info': effect.info}))

    def protobuf_to_effect(self, pb_effect):
        data = s11n.from_json(pb_effect.data)

        return Effect(id=pb_effect.id,
                      attribute=self.attribute_relation(pb_effect.attribute),
                      entity=pb_effect.entity,
                      value=s11n.from_json(pb_effect.value),
                      name=pb_effect.caption,
                      delta=data.get('delta'),
                      info=data.get('info'))

    def cmd_register(self, effect):
        answer = operations.sync_request(url=self.url('register'),
                                         data=tt_protocol_effects_pb2.RegisterRequest(effect=self.protobuf_from_effect(effect)),
                                         AnswerType=tt_protocol_effects_pb2.RegisterResponse)
        effect.id = answer.effect_id
        return answer.effect_id

    def cmd_remove(self, effect_id):
        operations.sync_request(url=self.url('remove'),
                                data=tt_protocol_effects_pb2.RemoveRequest(effect_id=effect_id),
                                AnswerType=tt_protocol_effects_pb2.RemoveResponse)

    def cmd_update(self, effect):
        operations.sync_request(url=self.url('update'),
                                data=tt_protocol_effects_pb2.UpdateRequest(effect=self.protobuf_from_effect(effect)),
                                AnswerType=tt_protocol_effects_pb2.UpdateResponse)

    def cmd_list(self):
        answer = operations.sync_request(url=self.url('list'),
                                         data=tt_protocol_effects_pb2.ListRequest(),
                                         AnswerType=tt_protocol_effects_pb2.ListResponse)

        return [self.protobuf_to_effect(pb_effect) for pb_effect in answer.effects]

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_effects_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_effects_pb2.DebugClearServiceResponse)
