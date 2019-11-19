

from tt_protocol.protocol import effects_pb2

from . import objects


def to_effect(pb_effect):
    return objects.Effect(id=pb_effect.id,
                          attribute=pb_effect.attribute,
                          entity=pb_effect.entity,
                          value=pb_effect.value,
                          caption=pb_effect.caption,
                          data=pb_effect.data)


def from_effect(effect):
    return effects_pb2.Effect(id=effect.id,
                              attribute=effect.attribute,
                              entity=effect.entity,
                              value=effect.value,
                              caption=effect.caption,
                              data=effect.data)
