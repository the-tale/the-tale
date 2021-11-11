
import datetime
import functools
import warnings

from aiohttp import web

from google.protobuf import any_pb2

from tt_protocol.protocol import base_pb2

from . import s11n
from . import log
from . import exceptions


def raw_api(extractor,
            ok_constructor,
            error_constructor):
    def decorator(handler):

        @functools.wraps(handler)
        async def wrapper(request):
            try:
                config = request.app['config']

                logger = log.ContextLogger()

                try:
                    request_message = await extractor(request, config, logger)

                except exceptions.ApiError:
                    raise

                except Exception:
                    logger.exception('Request message has unexpected format')
                    raise exceptions.ApiError(code='api.wrong_request_message',
                                              message='request message has unexpected format')

                response = await handler(request_message,
                                         config=config,
                                         logger=logger)

                if not isinstance(response, web.Response):
                    response = ok_constructor(response)

                return response

            except exceptions.ApiError as e:
                logger.exception('Error "%s" while processing request: %s (%s)', e.code, e.message, e.details)
                return error_constructor(code=e.code, message=e.message, details=e.details)

            except Exception:
                logger.exception('Unkown error occured during request processing')
                return error_constructor(code='api.unknown_error',
                                       message='unkown error occured during request processing',
                                       details={})

        return wrapper

    return decorator


##########
# JSON API
##########

async def json_extractor(request, config, logger):
    content = await request.content.read()
    return s11n.to_json(content)


def json_ok(message):
    return web.Response(content_type='application/json',
                        status=200,
                        body=s11n.to_json(message))


def json_error(code, message, details):
    data = {'code': code,
            'message': message,
            'details': details}

    return web.Response(content_type='application/json',
                        status=500,
                        body=s11n.to_json(data))


def json_api(extractor=json_extractor,
             ok_constructor=json_ok,
             error_constructor=json_error):
    return raw_api(extractor=extractor,
                   ok_constructor=ok_constructor,
                   error_constructor=error_constructor)


##############
# protobuf API
##############

def protobuf_extractor(ExpectedMessage):

    async def extractor(request, config, logger):
        content = await request.content.read()
        return ExpectedMessage.FromString(content)

    return extractor


def protobuf_ok(message):
    data = any_pb2.Any()
    data.Pack(message)

    body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                status=base_pb2.ApiResponse.SUCCESS,
                                data=data).SerializeToString()

    return web.Response(content_type='application/protobuf',
                        status=200,
                        body=body)


def protobuf_raw_ok(message):
    return web.Response(content_type='application/protobuf',
                        status=200,
                        body=message.SerializeToString())


def protobuf_error(code, message, details):
    error = base_pb2.ApiError(code=code, message=message, details=details)
    body = base_pb2.ApiResponse(server_time=datetime.datetime.now().timestamp(),
                                status=base_pb2.ApiResponse.ERROR,
                                error=error).SerializeToString()
    return web.Response(content_type='application/protobuf',
                        status=200,
                        body=body)


def protobuf_api(ExpectedMessage, raw=False):
    ok_constructor = protobuf_ok

    if raw:
        ok_constructor = protobuf_raw_ok

    return raw_api(extractor=protobuf_extractor(ExpectedMessage),
                   ok_constructor=ok_constructor,
                   error_constructor=protobuf_error)


# DEPRECATED
def api(ExpectedMessage, raw=False):
    warnings.warn('handlers.api method is deprecated, use handlers.protobuf_api instead',
                  DeprecationWarning)

    ok_constructor = protobuf_ok

    if raw:
        ok_constructor = protobuf_raw_ok

    return raw_api(extractor=protobuf_extractor(ExpectedMessage),
                   ok_constructor=ok_constructor,
                   error_constructor=protobuf_error)
