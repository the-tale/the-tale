# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: events_log.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='events_log.proto',
  package='events_log',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x10\x65vents_log.proto\x12\nevents_log\"K\n\x05\x45vent\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\x12\x0c\n\x04tags\x18\x03 \x03(\x04\x12\x0c\n\x04turn\x18\x04 \x01(\x04\x12\x0c\n\x04time\x18\x05 \x01(\x01\"I\n\x0f\x41\x64\x64\x45ventRequest\x12\x0c\n\x04tags\x18\x01 \x03(\x04\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\x12\x0c\n\x04turn\x18\x03 \x01(\x04\x12\x0c\n\x04time\x18\x04 \x01(\x01\"\x12\n\x10\x41\x64\x64\x45ventResponse\"G\n\x10GetEventsRequest\x12\x0c\n\x04tags\x18\x01 \x03(\x04\x12\x0c\n\x04page\x18\x02 \x01(\x04\x12\x17\n\x0frecords_on_page\x18\x03 \x01(\r\"[\n\x11GetEventsResponse\x12!\n\x06\x65vents\x18\x01 \x03(\x0b\x32\x11.events_log.Event\x12\x0c\n\x04page\x18\x02 \x01(\x04\x12\x15\n\rtotal_records\x18\x03 \x01(\x04\"4\n\x14GetLastEventsRequest\x12\x0c\n\x04tags\x18\x01 \x03(\x04\x12\x0e\n\x06number\x18\x02 \x01(\r\"Q\n\x15GetLastEventsResponse\x12!\n\x06\x65vents\x18\x01 \x03(\x0b\x32\x11.events_log.Event\x12\x15\n\rtotal_records\x18\x02 \x01(\x04\"\x1a\n\x18\x44\x65\x62ugClearServiceRequest\"\x1b\n\x19\x44\x65\x62ugClearServiceResponseb\x06proto3'
)




_EVENT = _descriptor.Descriptor(
  name='Event',
  full_name='events_log.Event',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='events_log.Event.id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='events_log.Event.data', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='events_log.Event.tags', index=2,
      number=3, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='turn', full_name='events_log.Event.turn', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='time', full_name='events_log.Event.time', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=32,
  serialized_end=107,
)


_ADDEVENTREQUEST = _descriptor.Descriptor(
  name='AddEventRequest',
  full_name='events_log.AddEventRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='tags', full_name='events_log.AddEventRequest.tags', index=0,
      number=1, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='events_log.AddEventRequest.data', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='turn', full_name='events_log.AddEventRequest.turn', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='time', full_name='events_log.AddEventRequest.time', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=109,
  serialized_end=182,
)


_ADDEVENTRESPONSE = _descriptor.Descriptor(
  name='AddEventResponse',
  full_name='events_log.AddEventResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=184,
  serialized_end=202,
)


_GETEVENTSREQUEST = _descriptor.Descriptor(
  name='GetEventsRequest',
  full_name='events_log.GetEventsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='tags', full_name='events_log.GetEventsRequest.tags', index=0,
      number=1, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='page', full_name='events_log.GetEventsRequest.page', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='records_on_page', full_name='events_log.GetEventsRequest.records_on_page', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=204,
  serialized_end=275,
)


_GETEVENTSRESPONSE = _descriptor.Descriptor(
  name='GetEventsResponse',
  full_name='events_log.GetEventsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='events', full_name='events_log.GetEventsResponse.events', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='page', full_name='events_log.GetEventsResponse.page', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_records', full_name='events_log.GetEventsResponse.total_records', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=277,
  serialized_end=368,
)


_GETLASTEVENTSREQUEST = _descriptor.Descriptor(
  name='GetLastEventsRequest',
  full_name='events_log.GetLastEventsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='tags', full_name='events_log.GetLastEventsRequest.tags', index=0,
      number=1, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='number', full_name='events_log.GetLastEventsRequest.number', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=370,
  serialized_end=422,
)


_GETLASTEVENTSRESPONSE = _descriptor.Descriptor(
  name='GetLastEventsResponse',
  full_name='events_log.GetLastEventsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='events', full_name='events_log.GetLastEventsResponse.events', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_records', full_name='events_log.GetLastEventsResponse.total_records', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=424,
  serialized_end=505,
)


_DEBUGCLEARSERVICEREQUEST = _descriptor.Descriptor(
  name='DebugClearServiceRequest',
  full_name='events_log.DebugClearServiceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=507,
  serialized_end=533,
)


_DEBUGCLEARSERVICERESPONSE = _descriptor.Descriptor(
  name='DebugClearServiceResponse',
  full_name='events_log.DebugClearServiceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=535,
  serialized_end=562,
)

_GETEVENTSRESPONSE.fields_by_name['events'].message_type = _EVENT
_GETLASTEVENTSRESPONSE.fields_by_name['events'].message_type = _EVENT
DESCRIPTOR.message_types_by_name['Event'] = _EVENT
DESCRIPTOR.message_types_by_name['AddEventRequest'] = _ADDEVENTREQUEST
DESCRIPTOR.message_types_by_name['AddEventResponse'] = _ADDEVENTRESPONSE
DESCRIPTOR.message_types_by_name['GetEventsRequest'] = _GETEVENTSREQUEST
DESCRIPTOR.message_types_by_name['GetEventsResponse'] = _GETEVENTSRESPONSE
DESCRIPTOR.message_types_by_name['GetLastEventsRequest'] = _GETLASTEVENTSREQUEST
DESCRIPTOR.message_types_by_name['GetLastEventsResponse'] = _GETLASTEVENTSRESPONSE
DESCRIPTOR.message_types_by_name['DebugClearServiceRequest'] = _DEBUGCLEARSERVICEREQUEST
DESCRIPTOR.message_types_by_name['DebugClearServiceResponse'] = _DEBUGCLEARSERVICERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Event = _reflection.GeneratedProtocolMessageType('Event', (_message.Message,), {
  'DESCRIPTOR' : _EVENT,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.Event)
  })
_sym_db.RegisterMessage(Event)

AddEventRequest = _reflection.GeneratedProtocolMessageType('AddEventRequest', (_message.Message,), {
  'DESCRIPTOR' : _ADDEVENTREQUEST,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.AddEventRequest)
  })
_sym_db.RegisterMessage(AddEventRequest)

AddEventResponse = _reflection.GeneratedProtocolMessageType('AddEventResponse', (_message.Message,), {
  'DESCRIPTOR' : _ADDEVENTRESPONSE,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.AddEventResponse)
  })
_sym_db.RegisterMessage(AddEventResponse)

GetEventsRequest = _reflection.GeneratedProtocolMessageType('GetEventsRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETEVENTSREQUEST,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.GetEventsRequest)
  })
_sym_db.RegisterMessage(GetEventsRequest)

GetEventsResponse = _reflection.GeneratedProtocolMessageType('GetEventsResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETEVENTSRESPONSE,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.GetEventsResponse)
  })
_sym_db.RegisterMessage(GetEventsResponse)

GetLastEventsRequest = _reflection.GeneratedProtocolMessageType('GetLastEventsRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETLASTEVENTSREQUEST,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.GetLastEventsRequest)
  })
_sym_db.RegisterMessage(GetLastEventsRequest)

GetLastEventsResponse = _reflection.GeneratedProtocolMessageType('GetLastEventsResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETLASTEVENTSRESPONSE,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.GetLastEventsResponse)
  })
_sym_db.RegisterMessage(GetLastEventsResponse)

DebugClearServiceRequest = _reflection.GeneratedProtocolMessageType('DebugClearServiceRequest', (_message.Message,), {
  'DESCRIPTOR' : _DEBUGCLEARSERVICEREQUEST,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.DebugClearServiceRequest)
  })
_sym_db.RegisterMessage(DebugClearServiceRequest)

DebugClearServiceResponse = _reflection.GeneratedProtocolMessageType('DebugClearServiceResponse', (_message.Message,), {
  'DESCRIPTOR' : _DEBUGCLEARSERVICERESPONSE,
  '__module__' : 'events_log_pb2'
  # @@protoc_insertion_point(class_scope:events_log.DebugClearServiceResponse)
  })
_sym_db.RegisterMessage(DebugClearServiceResponse)


# @@protoc_insertion_point(module_scope)
