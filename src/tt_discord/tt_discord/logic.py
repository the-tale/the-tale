
import re

from tt_web import log
from tt_web.common import event

from . import bot
from . import conf
from . import operations


# https://discordapp.com/developers/docs/resources/user
def normalize_nickname(nickname, error_nick='unknown player', replacer='?'):
    nickname = nickname.strip()

    nickname = re.sub('\s+', ' ', nickname)

    if nickname in ('discordtag', 'everyone', 'here'):
        return error_nick

    for substring in ('@', '#', ':', '```'):
        nickname = nickname.replace(substring, replacer * len(substring))

    if nickname == '':
        return error_nick

    return nickname[:conf.DISCORD_NICKNAME_MAX_LENGTH]


###################
# TODO: write tests
###################

async def _sync_data(bot_instance, config, logger):

    changes = await operations.get_any_new_game_data(config['sync_users_chank_size'])

    if not changes:
        logger.info('synchonisation: no changes detected, wait for changes')
        return False

    logger.info('synchonisation: changes found (%s)', len(changes))

    for change in changes:
        logger.info('synchonisation: process change <%s>', change)
        await bot.sync_change(change, bot_instance, config, logger=logger)
        logger.info('synchonisation: change processed')

    logger.info('synchonisation: all changes processed')

    return True


async def _sync_orphan_discords(bot_instance, config, logger):
    logger.info('synchonisation: look for orphan discord accounts')

    accounts_to_remove = await operations.get_orphan_discord_accounts()

    logger.info('synchonisation: %s orphan discord accounts found, try to remove', len(accounts_to_remove))

    for account_info in accounts_to_remove:
        logger.info('synchonisation: try to remove account %s', account_info)

        await bot.reset_discord_properties(bot_instance, account_info.discord_id, logger=logger)

        await operations.delete_account(account_info.id)

    return bool(accounts_to_remove)


async def sync_users(bot_instance, config):

    logger = log.ContextLogger()

    logger.info('synchonisation: start')

    sync_event = event.get(conf.SYNC_EVENT_NAME)

    while True:
        sync_event.clear()

        data_synced = await _sync_data(bot_instance, config, logger=logger)

        orphans_removed = await _sync_orphan_discords(bot_instance, config, logger=logger)

        if data_synced or orphans_removed:
            logger.info('synchonisation: go to next iteration')
            sync_event.set()
            continue

        logger.info('synchonisation: wait for updates')

        await sync_event.wait()


async def remove_account_data(account_info):
    if account_info.discord_id is not None:
        # unvind will raise conf.SYNC_EVENT_NAME event and force sync_users to update (reset) orphan data
        await operations.unbind_discord_user(discord_id=account_info.discord_id)
