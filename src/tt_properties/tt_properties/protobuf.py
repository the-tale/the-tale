
from tt_protocol.protocol import properties_pb2

from . import objects
from . import relations


def to_property(pb_property):
    return objects.Property(object_id=pb_property.object_id,
                            type=pb_property.type,
                            value=pb_property.value,
                            mode=relations.MODE(pb_property.mode))


def from_property(property):
    return properties_pb2.Property(object_id=property.object_id,
                                   type=property.type,
                                   value=property.value,
                                   mode=properties_pb2.Property.Mode.UNKNOWN)
