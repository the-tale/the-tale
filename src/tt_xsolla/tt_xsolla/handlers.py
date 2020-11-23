
import re
import hashlib

from aiohttp import web

from tt_web import s11n
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import xsolla_pb2
from tt_protocol.protocol import data_protector_pb2

from . import xsolla
from . import protobuf
from . import logic
from . import operations


##############
# external API
##############

# signature documentation
# https://developers.xsolla.com/ru/api/v2/getting-started/#api_webhooks_signing_requests

SIGNATURE_REGEX = re.compile(r'^\s*Signature\s*([^\s]+)')


def get_auth_signature(header):
    match = SIGNATURE_REGEX.match(header)

    if match is None:
        return None

    return match.group(1)


def get_expected_auth_signature(content, key):
    h = hashlib.sha1()
    h.update(content)
    h.update(key.encode('utf-8'))
    return h.hexdigest()


async def xsolla_extractor(request, config, logger):
    content = await request.content.read()

    auth_header = request.headers.get('Authorization', '')

    request_signature = get_auth_signature(auth_header)

    if request_signature is None:
        raise tt_exceptions.ApiError(code='xsolla.hook.signature_has_not_found',
                                     message='signature has not found in headers',
                                     details={'AuthorisationHeader': auth_header})

    expected_signature = get_expected_auth_signature(content, config['custom']['hooks_key'])

    if request_signature != expected_signature:
        raise tt_exceptions.ApiError(code='xsolla.hook.unexpected_signature',
                                     message='Received signature does not equal to calculated',
                                     details={'AuthorisationHeader': auth_header})

    data = s11n.from_json(content)

    if 'settings' not in data:
        raise tt_exceptions.ApiError(code='xsolla.hook.no_settings_info',
                                     message='settings not found in request body')

    if data['settings'].get('project_id') != config['custom']['project_id']:
        raise tt_exceptions.ApiError(code='xsolla.hook.wrong_project_id',
                                     message='Unexpected project_id on request body')

    if data['settings'].get('merchant_id') != config['custom']['merchant_id']:
        raise tt_exceptions.ApiError(code='xsolla.hook.wrong_merchant_id',
                                     message='Unexpected merchant_id on request body')

    return data


def xsolla_ok(message):
    return web.Response(content_type='application/json',
                        status=204,
                        body=s11n.to_json(message))


def xsolla_error(code, message, details):
    data = {'code': code,
            'message': message,
            'details': details}

    status_code = 400

    if code == 'api.unknown_error':
        status_code = 500

    return web.Response(content_type='application/json',
                        status=status_code,
                        body=s11n.to_json(data))


def xsolla_api(extractor=xsolla_extractor,
               ok_constructor=xsolla_ok,
               error_constructor=xsolla_error):
    return handlers.raw_api(extractor=extractor,
                            ok_constructor=ok_constructor,
                            error_constructor=error_constructor)


@xsolla_api()
async def xsolla_hook(message, config, logger, **kwargs):

    notification_type = message.get('notification_type')

    if notification_type == 'user_validation':
        is_valid = await logic.validate_user(account_id=int(message['user']['id']),
                                             email=message['user']['email'],
                                             name=message['user']['name'])
        if not is_valid:
            raise tt_exceptions.ApiError(code='xsolla.hook.user_validation.account_not_found',
                                         message='Account with such credentials has not found')

    elif notification_type == 'payment':
        invoice = logic.invoice_from_xsolla_data(message)

        result = await logic.register_invoice(invoice)

        if result.is_error():
            raise tt_exceptions.ApiError(code='xsolla.hook.payment.can_not_register_invoice',
                                         message=f'Can not register invoice: {result.name}')

    elif notification_type == 'refund':
        result = await logic.register_cancellation(xsolla_id=message['transaction']['id'])

        if result.is_error():
            raise tt_exceptions.ApiError(code='xsolla.hook.refund.can_not_register_cancelation',
                                         message=f'Can not register cancelation: {result.name}')

    else:
        raise tt_exceptions.ApiError(code='xsolla.hook.unknown_notification_type',
                                     message='Service does not expect such notification type',
                                     details={'notification_type': notification_type})

    return {'result': 'ok'}


##############
# internal API
##############

@handlers.protobuf_api(xsolla_pb2.GetTokenRequest)
async def get_token(message, config, logger, **kwargs):

    account_info = protobuf.to_account_info(message.account_info)

    token = await logic.find_token(account_info, expiration_delta=config['custom']['token_expiration_delta'])

    if token.is_error('AccountRemovedByGDPR'):
        raise tt_exceptions.ApiError(code='xsolla.get_token.account_removed_by_gdpr',
                                     message='Account removed by user request and can not be processed')

    if token.is_error():
        logger.info('token not found: %s', token.name)

        xsolla_client = xsolla.get_client(config['custom'], mode=message.mode)

        token = await logic.request_token(account_info, xsolla_client, logger)

    if token.is_error():
        raise tt_exceptions.ApiError(code='xsolla.get_token.can_not_receive_token',
                                     message='Can not receive token from XSolla services')

    return xsolla_pb2.GetTokenResponse(token=token.value.value)


@handlers.api(data_protector_pb2.PluginReportRequest, raw=True)
async def data_protection_collect_data(message, config, **kwargs):

    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='xsolla.data_protection_collect_data.wrong_secret',
                                     message='wrong secret code')

    report = await logic.get_data_report(int(message.account_id))

    return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.ResultType.SUCCESS,
                                                   data=s11n.to_json(report))


@handlers.api(data_protector_pb2.PluginDeletionRequest, raw=True)
async def data_protection_delete_data(message, config, **kwargs):
    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='xsolla.data_protection_delete_data.wrong_secret',
                                     message='wrong secret code')

    await logic.delete_account_data(int(message.account_id))

    return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS)


@handlers.protobuf_api(xsolla_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return xsolla_pb2.DebugClearServiceResponse()
