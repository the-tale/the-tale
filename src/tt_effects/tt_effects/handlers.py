
from tt_web import handlers

from tt_protocol.protocol import effects_pb2

from . import protobuf
from . import operations


@handlers.api(effects_pb2.RegisterRequest)
async def register(message, **kwargs):
    effect_id = await operations.register_effect(effect=protobuf.to_effect(message.effect))
    return effects_pb2.RegisterResponse(effect_id=effect_id)


@handlers.api(effects_pb2.RemoveRequest)
async def remove(message, **kwargs):
    await operations.remove_effect(effect_id=message.effect_id)
    return effects_pb2.RemoveResponse()


@handlers.api(effects_pb2.UpdateRequest)
async def update(message, **kwargs):
    await operations.update_effect(effect=protobuf.to_effect(message.effect))
    return effects_pb2.UpdateResponse()


@handlers.api(effects_pb2.ListRequest)
async def list(message, **kwargs):
    effects = await operations.load_effects()
    return effects_pb2.ListResponse(effects=[protobuf.from_effect(effect) for effect in effects])


@handlers.api(effects_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return effects_pb2.DebugClearServiceResponse()
