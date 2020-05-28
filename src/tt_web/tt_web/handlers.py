
import datetime
import functools

from aiohttp import web

from google.protobuf import any_pb2

from tt_protocol.protocol import base_pb2

from . import exceptions


def api(ExpectedMessage, raw=False):

    def decorator(handler):

        @functools.wraps(handler)
        async def wrapper(request):
            try:
                content = await request.content.read()

                try:
                    request_message = ExpectedMessage.FromString(content)
                except Exception as e:
                    raise exceptions.ApiError(code='api.wrong_request_message', message='request message has unexpected format')

                response_message = await handler(request_message, config=request.app['config'])

                if not raw:
                    data = any_pb2.Any()
                    data.Pack(response_message)

                    body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                                status=base_pb2.ApiResponse.SUCCESS,
                                                data=data)
                else:
                    body = response_message

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
