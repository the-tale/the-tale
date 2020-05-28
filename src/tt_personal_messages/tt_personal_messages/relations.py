
import rels

from rels import django as django_rels

from tt_protocol.protocol import personal_messages_pb2


class OWNER_TYPE(django_rels.DjangoEnum):
    protocol_value = rels.Column(no_index=False)

    records = (('SENDER', 0, 'отправитель', personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['SENDER'].number),
               ('RECIPIENT', 1, 'получатель', personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['RECIPIENT'].number))
