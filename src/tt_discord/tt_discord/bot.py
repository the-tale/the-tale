
import uuid
import logging

from discord.ext import commands as discord_commands

from tt_web import log

from . import relations
from . import operations


REQUIRED_PERMISSIONS = {'manage_nicknames',
                        'manage_roles'}


class Bot(discord_commands.Bot):

    async def on_ready(self):
        logger = log.ContextLogger()

        logger.info('logged as "%s"', self.user)

        for guild in self.guilds:
            await self.check_permissions(guild)

        await self.reset_not_binded_user_properties(logger=logger)

    async def on_member_join(self, member):
        logging.info("user %s joind guild %s, try to update it's properties", member.id, member.guild.id)

        account_info = await operations.get_account_info_by_discord_id(member.id)

        await operations.force_game_data_update(account_info.id)

    async def on_command_error(self, context, error):
        if isinstance(error, discord_commands.CommandNotFound):
            await context.send(f'Не знаю команду {context.invoked_with}')
            return

        if isinstance(error, discord_commands.MissingRequiredArgument):
            await context.send(f'В команду {context.invoked_with} переданы не все аргументы')
            return

        if isinstance(error, discord_commands.BadArgument):
            await context.send(f'В команду {context.invoked_with} один из аргументов передан в неверном формате')
            return

        return await super().on_command_error(context, error)

    async def check_permissions(self, guild):
        member = guild.get_member(self.user.id)

        for name in REQUIRED_PERMISSIONS:
            if not getattr(member.guild_permissions, name):
                logging.error('Bot has no permission "%(permission)s" on guild "%(guild_name)s" [%(guild_id)s]',
                              {'permission': name,
                               'guild_name': guild.name,
                               'guild_id': guild.id})

    async def reset_not_binded_user_properties(self, logger):
        logger.info('reset properties of unbinded members')

        for guild in self.guilds:
            for member in guild.members:

                if guild.owner.id == member.id:
                    continue

                account_info = await operations.get_account_info_by_discord_id(member.id)

                if account_info.game_id is None:
                    await reset_discord_properties(self, member.id, logger=logger)

        logger.info('properties on unbinded members reseted')


class HelpCommand(discord_commands.DefaultHelpCommand):

    def __init__(self,
                 commands_heading='Команды:',
                 no_category='Команды',
                 command_attrs={'help': 'Отобразить этот текст.'},
                 **kwargs):
        super().__init__(commands_heading=commands_heading,
                         no_category=no_category,
                         command_attrs=command_attrs,
                         **kwargs)

    def get_ending_note(self):
        return f'Введите "{self.clean_prefix}{self.invoked_with} <команда>", чтобы получить подробную информацию о команде.'


DESCRIPTION = '''
Это бот игры «Сказка»: https://the-tale.org

Он синхронизирует статус игроков в Discord со статусом в игре.

Подробную информацию о возможностях бота можно найти на странице: https://the-tale.org/chat

'''


def construct(config):

    bot = Bot(command_prefix=config['command_prefix'],
              description=DESCRIPTION.strip(),
              help_command=HelpCommand(),
              command_not_found='Команда "{}" не найдена.')

    @bot.command(help='Прикрепляет ваш аккаунт в игре к аккаунту в Discord. Вводите эту команду так, как её отобразила игра.',
                 brief='Прикрепляет ваш аккаунт в игре к аккаунту в Discord.')
    async def bind(context, bind_code: uuid.UUID):
        await command_bind(context, bind_code)
        await context.send('команда выполнена')

    @bot.command(help='Удаляет связь вашего аккаунта в игре с аккаунтом в Discord. Сбрасывает все параметры, перенесённые из игры.',
                 brief='Удаляет связь вашего аккаунта в игре с аккаунтом в Discord.')
    async def unbind(context):
        await command_unbind(context)
        await context.send('команда выполнена')

    return bot


async def command_bind(context, bind_code):
    logging.info('bind command received, code: "%s", discord id: "%s"', bind_code, context.author.id)

    result = await operations.bind_discord_user(bind_code=bind_code,
                                                discord_id=context.author.id)

    if result not in relations.BIND_RESULT_MESSAGES:
        raise NotImplementedError('unknown bind result')

    await context.send(relations.BIND_RESULT_MESSAGES[result])

    if not result.is_success():
        return


async def command_unbind(context):
    logging.info('unbind command received, discord id: "%s"', context.author.id)

    await operations.unbind_discord_user(discord_id=context.author.id)


async def sync_change(change, bot, config, logger):

    account_info = await operations.get_account_info_by_id(change['account_id'])

    if not account_info.is_binded():
        NotImplementedError('game account not bind to discord')

    if change['type'] is relations.GAME_DATA_TYPE.NICKNAME:
        await sync_nickname(bot, account_info, change['data'], logger=logger)

    elif change['type'] is relations.GAME_DATA_TYPE.ROLES:
        await sync_roles(bot, account_info, change['data'], config=config, logger=logger)

    elif change['type'] is relations.GAME_DATA_TYPE.BAN:
        await sync_ban(bot, account_info, change['data'], config=config, logger=logger)

    await operations.mark_game_data_synced(account_info.id,
                                           type=change['type'],
                                           synced_at=change['updated_at'])


async def sync_nickname(bot, account_info, data, logger):

    nickname = data['nickname']

    for guild in bot.guilds:
        member = guild.get_member(account_info.discord_id)

        if member is None:
            logger.info('discord user %s not found in guild %s', account_info.discord_id, guild.id)
            continue

        if guild.owner.id == member.id:
            await member.send('Я не могу изменить ваш ник, так как вы являетесь владельцем сервера.')
            continue

        await member.edit(nick=nickname, reason='Синхронизация с ником в игре.')
        await member.send('Я изменил ваш ник, чтобы он соответствовал нику в игре.')


async def sync_roles(bot, account_info, data, config, logger):

    roles = data['roles']

    for guild in bot.guilds:
        member = guild.get_member(account_info.discord_id)

        if member is None:
            logger.info('discord user %s not found in guild %s', account_info.discord_id, guild.id)
            continue

        discord_roles = []

        for name in roles:
            if name not in config['roles']:
                logger.error('Role "%(role)s" does not defined in config', {'role': name})
                continue

            discord_roles.append(guild.get_role(int(config['roles'][name])))

        await member.edit(roles=discord_roles, reason='Синхронизация с ролями в игре.')
        await member.send('Я изменил ваши роли, чтобы они соответствовали статусу в игре.')


async def sync_ban(bot, account_info, data, config, logger):

    if not data['ban']:
        return

    for guild in bot.guilds:
        member = guild.get_member(account_info.discord_id)

        if member is None:
            logger.info('discord user %s not found in guild %s', account_info.discord_id, guild.id)
            continue

        if member.bot:
            logger.info('can not ban bot %s in guid %s', account_info.discord_id, guild.id)
            continue

        if guild.owner.id == member.id:
            logger.info('can not ban owner of guid %s', account_info.discord_id, guild.id)
            continue

        await member.ban(reason='Вы звбанены в Discord из-за бана в игре. Чтобы снять бан — обратитесь к администрации игры ПОСЛЕ окончания бана в ней. ')


async def reset_discord_properties(bot, discord_id, logger):

    for guild in bot.guilds:
        member = guild.get_member(discord_id)

        if member is None:
            logger.info('discord user %s not found in guild %s', account_info.discord_id, guild.id)
            continue

        logger.error('reset properties of user %s on guild %s', discord_id, guild.id)

        arguments = {}

        if guild.owner.id != member.id:
            arguments['nick'] = None

        if not member.bot:
            arguments['roles'] = []

        await member.edit(**arguments,
                          reason='Сброс синхронизации с игрой.')
