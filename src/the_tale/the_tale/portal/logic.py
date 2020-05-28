
import smart_imports

smart_imports.all()


def cdn_paths():

    if django_settings.CDNS_ENABLED and conf.settings.SETTINGS_CDN_INFO_KEY in global_settings:
        return s11n.from_json(global_settings[conf.settings.SETTINGS_CDN_INFO_KEY])

    return utils_cdn.get_local_paths(django_settings.CDNS)


def new_day_actions():
    accounts_query = accounts_prototypes.AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now(),
                                                                              ban_game_end_at__lt=datetime.datetime.now(),
                                                                              ban_forum_end_at__lt=datetime.datetime.now(),
                                                                              premium_end_at__lt=datetime.datetime.now())

    accounts_number = accounts_query.count()
    if accounts_number < 1:
        return

    account = None

    for i in range(1000):
        account_model = accounts_query[random.randint(0, accounts_number - 1)]
        account = accounts_prototypes.AccountPrototype(model=account_model)

        # explicity check for premium, since infinit subscribers does not filtered by previouse query
        if not account.is_premium:
            break
    else:
        return  # if not premium account does not found

    global_settings[conf.settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY] = str(account.id)

    account.prolong_premium(days=conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY)

    message = '''
Поздравляем!

Ваш герой выбран героем дня и Вы получаете %(days)d дней подписки!
''' % {'days': conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY}

    personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                         recipients_ids=[account.id],
                                         body=message,
                                         asynchronous=True)


def sync_with_discord(account):
    tt_services.discord.cmd_update_user(discord.construct_user_info(account))
