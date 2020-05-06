
import smart_imports

smart_imports.all()


class DISCORD_ROLE(rels_django.DjangoEnum):
    description = rels.Column()
    rights_description = rels.Column(unique=False)

    records = (('DEVELOPER', 0, 'Разработчик', 'Разработчик игры.',
                'Может добавлять реакции на сообщения, загружать файлы, использовать эмодзи с других серверов, использовать команды @everyone и @here. Может управлять слышимостью Хранителей в голосовых каналах.'),
               ('MODERATOR', 1, 'Модератор', 'Модератор из состава игроков.',
                'Может добавлять реакции на сообщения, загружать файлы, использовать эмодзи с других серверов, использовать команды @everyone и @here. Может управлять слышимостью Хранителей в голосовых каналах.'),
               ('PILLAR_OF_WORLD', 2, 'Столп Мира', 'Хранитель, имеющий 10000 могущества или более.',
                'Может добавлять реакции на сообщения, загружать файлы, использовать эмодзи с других серверов, использовать команды @everyone и @here. Может управлять слышимостью Хранителей в голосовых каналах.'),
               ('MIGHTY_KEEPER', 3, 'Могучий Хранитель', 'Хранитель, имеющий 1000 могущества или более.',
                'Может добавлять реакции на сообщения, загружать файлы, использовать эмодзи с других серверов, использовать команды @everyone и @here.'),
               ('KEEPER', 4, 'Хранитель', 'Хранитель, имеющий 100 могущества или более.',
                'Может добавлять реакции на сообщения, загружать файлы, использовать эмодзи с других серверов, использовать команды @everyone и @here.'),
               ('SPIRIT_OF_PANDORA', 5, 'Дух Пандоры', 'Хранитель, связавший аккаунт в игре с аккаунтом в Discord.',
                'Может добавлять реакции на сообщения, загружать файлы.'),
               ('CLAN_COMMAND', 6, 'Командование гильдии', 'Хранитель является магистром или командором гильдии.', ''))


def construct_user_info(account):

    ##########
    # nickname
    ##########
    nickname = account.nick_verbose

    if account.clan_id is not None:
        membership = clans_logic.get_membership(account.id)
        nickname = f'[{clans_storage.infos[account.clan_id].abbr}] {membership.role.symbol} {nickname}'

    #######
    # roles
    #######

    roles = set()

    if account.id in accounts_conf.settings.DEVELOPERS_IDS:
        roles.add(DISCORD_ROLE.DEVELOPER)

    if account.id in accounts_conf.settings.MODERATORS_IDS:
        roles.add(DISCORD_ROLE.MODERATOR)

    membership = clans_logic.get_membership(account.id)

    if membership is not None and (membership.role.is_MASTER or membership.role.is_COMANDOR):
        roles.add(DISCORD_ROLE.CLAN_COMMAND)

    if account.might >= 10000:
        roles.add(DISCORD_ROLE.PILLAR_OF_WORLD)

    elif account.might >= 1000:
        roles.add(DISCORD_ROLE.MIGHTY_KEEPER)

    elif account.might >= 100:
        roles.add(DISCORD_ROLE.KEEPER)

    else:
        roles.add(DISCORD_ROLE.SPIRIT_OF_PANDORA)

    ################
    # construct user
    ################
    user = tt_protocol_discord_pb2.User(id=account.id,
                                        nickname=nickname,
                                        roles=[role.name.lower() for role in roles],
                                        banned=account.is_ban_forum)

    return user
