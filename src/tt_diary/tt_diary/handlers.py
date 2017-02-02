
from tt_web import handlers

from tt_protocol.protocol import diary_pb2

from . import objects
from . import protobuf
from . import operations


@handlers.api(diary_pb2.VersionRequest)
async def version(message, **kwargs):
    version = operations.TIMESTAMPS_CACHE.get(message.account_id, 0)
    return diary_pb2.VersionResponse(version=version)


@handlers.api(diary_pb2.PushMessageRequest)
async def push_message(message, **kwargs):
    await operations.push_message(account_id=message.account_id,
                                  diary_size=message.diary_size,
                                  message=protobuf.to_message(message.message))
    return diary_pb2.PushMessageResponse()


@handlers.api(diary_pb2.DiaryRequest)
async def diary(message, **kwargs):
    diary = await operations.load_diary(account_id=message.account_id)

    if diary is None:
        diary = objects.Diary()

    return diary_pb2.DiaryResponse(diary=protobuf.from_diary(diary))
