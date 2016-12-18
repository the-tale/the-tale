
import datetime
import functools

from aiohttp import web

from google.protobuf import any_pb2

from tt_protocol.protocol import base_pb2
from tt_protocol.protocol import diary_pb2

from . import objects
from . import protobuf
from . import operations
from . import exceptions



def api(ExpectedMessage):

    def decorator(handler):

        @functools.wraps(handler)
        async def wrapper(request):
            try:
                content = await request.content.read()

                try:
                    request_message = ExpectedMessage.FromString(content)
                except Exception as e:
                    raise exceptions.ApiError(code='api.wrong_request_message', message='request message has unexpected format')

                response_message = await handler(request_message)

                data = any_pb2.Any()
                data.Pack(response_message)

                body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                            status=base_pb2.ApiResponse.SUCCESS,
                                            data=data)

            except exceptions.ApiError as e:
                error = base_pb2.ApiError(code=e.code, message=e.message, details=e.details)

                body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                            status=base_pb2.ApiResponse.ERROR,
                                            error=error)

            except Exception as e:
                import traceback
                traceback.print_exc()

                error = base_pb2.ApiError(code='api.unknown_error', message='unkown error occured during request processing', details={})
                body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                            status=base_pb2.ApiResponse.ERROR,
                                            error=error)

            finally:
                return web.Response(content_type='application/protobuf',
                                    body=body.SerializeToString())



        return wrapper

    return decorator


@api(diary_pb2.VersionRequest)
async def version(message, **kwargs):
    version = operations.TIMESTAMPS_CACHE.get(message.account_id, 0)
    return diary_pb2.VersionResponse(version=version)


@api(diary_pb2.PushMessageRequest)
async def push_message(message, **kwargs):
    await operations.push_message(account_id=message.account_id,
                                  diary_size=message.diary_size,
                                  message=protobuf.to_message(message.message))
    return diary_pb2.PushMessageResponse()


@api(diary_pb2.DiaryRequest)
async def diary(message, **kwargs):
    diary = await operations.load_diary(account_id=message.account_id)

    if diary is None:
        diary = objects.Diary()

    return diary_pb2.DiaryResponse(diary=protobuf.from_diary(diary))
