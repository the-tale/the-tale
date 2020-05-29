
from tt_web import log
from tt_web import s11n
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import discord_pb2
from tt_protocol.protocol import data_protector_pb2

from . import logic
from . import protobuf
from . import operations


async def sync_user(user, create_if_not_exists, logger, force=False):

    account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists)

    logger.info('try to sync data of user %s, create_if_not_exists: %s, force: %s',
                account_info, create_if_not_exists, force)

    if account_info.id is None:
        logger.info('user account not created, no need to store data')
        return account_info

    nickname = logic.normalize_nickname(user.nickname)

    logger.info('normalize user %s nickname: %s', account_info.id, nickname)

    data = {'nickname': nickname,
            'roles': list(user.roles)}

    if user.banned:
        # permanently mark account as banned
        # see https://github.com/the-tale/the-tale/issues/2518 for details
        data['ban'] = True

    await operations.update_game_data(account_info.id,
                                      **data,
                                      force=force,
                                      logger=logger)

    return account_info


@handlers.api(discord_pb2.GetBindCodeRequest)
async def get_bind_code(message, **kwargs):
    logger = log.ContextLogger()

    account_info = await sync_user(message.user,
                                   create_if_not_exists=True,
                                   force=True,
                                   logger=logger)

    bind_code = await operations.get_bind_code(account_info.id, expire_timeout=message.expire_timeout)

    return discord_pb2.GetBindCodeResponse(code=protobuf.from_bind_code(bind_code))


@handlers.api(discord_pb2.UpdateUserRequest)
async def update_user(message, **kwargs):
    logger = log.ContextLogger()

    await sync_user(message.user,
                    create_if_not_exists=False,
                    force=message.force,
                    logger=logger)

    return discord_pb2.UpdateUserResponse()


@handlers.api(data_protector_pb2.PluginReportRequest, raw=True)
async def data_protection_collect_data(message, config, **kwargs):

    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='discord.data_protection_collect_data.wrong_secret',
                                     message='wrong secret code')

    account_info = await operations.get_account_info_by_game_id(int(message.account_id),
                                                                create_if_not_exists=False)

    report = await operations.get_data_report(account_info=account_info)

    return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.ResultType.SUCCESS,
                                                   data=s11n.to_json(report))


@handlers.api(data_protector_pb2.PluginDeletionRequest, raw=True)
async def data_protection_delete_data(message, config, **kwargs):
    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='discord.data_protection_delete_data.wrong_secret',
                                     message='wrong secret code')

    account_info = await operations.get_account_info_by_game_id(int(message.account_id),
                                                                create_if_not_exists=False)

    if account_info.discord_id is not None:
        await operations.unbind_discord_user(discord_id=account_info.discord_id)

    return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS)


@handlers.api(discord_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return discord_pb2.DebugClearServiceResponse()
