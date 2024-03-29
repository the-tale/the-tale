# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: uniquer.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='uniquer.proto',
  package='uniquer',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\runiquer.proto\x12\x07uniquer\"\x1b\n\x0cGetIdRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\"\"\n\rGetIdResponse\x12\x11\n\tunique_id\x18\x01 \x01(\x03\"\x1a\n\x18\x44\x65\x62ugClearServiceRequest\"\x1b\n\x19\x44\x65\x62ugClearServiceResponseb\x06proto3'
)




_GETIDREQUEST = _descriptor.Descriptor(
  name='GetIdRequest',
  full_name='uniquer.GetIdRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='uniquer.GetIdRequest.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=26,
  serialized_end=53,
)


_GETIDRESPONSE = _descriptor.Descriptor(
  name='GetIdResponse',
  full_name='uniquer.GetIdResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='unique_id', full_name='uniquer.GetIdResponse.unique_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
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
  serialized_start=55,
  serialized_end=89,
)


_DEBUGCLEARSERVICEREQUEST = _descriptor.Descriptor(
  name='DebugClearServiceRequest',
  full_name='uniquer.DebugClearServiceRequest',
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
  serialized_start=91,
  serialized_end=117,
)


_DEBUGCLEARSERVICERESPONSE = _descriptor.Descriptor(
  name='DebugClearServiceResponse',
  full_name='uniquer.DebugClearServiceResponse',
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
  serialized_start=119,
  serialized_end=146,
)

DESCRIPTOR.message_types_by_name['GetIdRequest'] = _GETIDREQUEST
DESCRIPTOR.message_types_by_name['GetIdResponse'] = _GETIDRESPONSE
DESCRIPTOR.message_types_by_name['DebugClearServiceRequest'] = _DEBUGCLEARSERVICEREQUEST
DESCRIPTOR.message_types_by_name['DebugClearServiceResponse'] = _DEBUGCLEARSERVICERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetIdRequest = _reflection.GeneratedProtocolMessageType('GetIdRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETIDREQUEST,
  '__module__' : 'uniquer_pb2'
  # @@protoc_insertion_point(class_scope:uniquer.GetIdRequest)
  })
_sym_db.RegisterMessage(GetIdRequest)

GetIdResponse = _reflection.GeneratedProtocolMessageType('GetIdResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETIDRESPONSE,
  '__module__' : 'uniquer_pb2'
  # @@protoc_insertion_point(class_scope:uniquer.GetIdResponse)
  })
_sym_db.RegisterMessage(GetIdResponse)

DebugClearServiceRequest = _reflection.GeneratedProtocolMessageType('DebugClearServiceRequest', (_message.Message,), {
  'DESCRIPTOR' : _DEBUGCLEARSERVICEREQUEST,
  '__module__' : 'uniquer_pb2'
  # @@protoc_insertion_point(class_scope:uniquer.DebugClearServiceRequest)
  })
_sym_db.RegisterMessage(DebugClearServiceRequest)

DebugClearServiceResponse = _reflection.GeneratedProtocolMessageType('DebugClearServiceResponse', (_message.Message,), {
  'DESCRIPTOR' : _DEBUGCLEARSERVICERESPONSE,
  '__module__' : 'uniquer_pb2'
  # @@protoc_insertion_point(class_scope:uniquer.DebugClearServiceResponse)
  })
_sym_db.RegisterMessage(DebugClearServiceResponse)


# @@protoc_insertion_point(module_scope)
