
import smart_imports

smart_imports.all()


##############
# collect data
##############

def postprocess_record(record):
    if record[0] == 'tt_players_properties':
        new_record = copy.deepcopy(record)
        new_record[2]['type'] = tt_services.PLAYER_PROPERTIES(new_record[2]['type']).text
        return new_record

    return record


def postprocess_value(value):

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(key): postprocess_value(subvalue)
                for key, subvalue in value.items()}

    if isinstance(value, rels.Record):
        return value.text

    if isinstance(value, (list, tuple)):
        return [postprocess_value(subvalue) for subvalue in value]

    return value


def collect_account_data(account_id):
    data = []

    account = prototypes.AccountPrototype.get_by_id(account_id)

    data.append(('nick', account.nick_verbose))
    data.append(('description', account.description))
    data.append(('last_news_remind_time', account.last_news_remind_time))
    data.append(('gender', account.gender))

    data.append(('infinit_subscription', account.is_premium_infinit))
    if not account.is_premium_infinit:
        data.append(('subscription_end_at', account.premium_end_at))

    data.append(('subscription_expired_notification_send_at', account._model.premium_expired_notification_send_at))

    data.append(('active_end_at', account.active_end_at))
    data.append(('ban_game_end_at', account.ban_game_end_at if account.is_ban_game else None))
    data.append(('ban_forum_end_at', account.ban_forum_end_at if account.is_ban_forum else None))

    data.append(('created_at', account.created_at))
    data.append(('updated_at', account._model.updated_at))

    data.append(('email', account.email))

    data.append(('personal_messages_subscription', account.personal_messages_subscription))
    data.append(('news_subscription', account.news_subscription))

    data.append(('referer_domain', account.referer_domain))
    data.append(('referer', account.referer))

    data.append(('referral_of', account.referral_of_id))
    data.append(('referrals_number', account.referrals_number))

    data.append(('action_id', account.action_id))

    return data


def collect_might_data(account_id):
    data = []

    for award in models.Award.objects.filter(account=account_id):
        data.append(('mights', {'type': award.type,
                                'description': award.description,
                                'created_at': award.created_at,
                                'updated_at': award.updated_at}))

    return data


def collect_reset_password_data(account_id):
    data = []

    for reset_task in models.ResetPasswordTask.objects.filter(account=account_id):
        data.append(('reset_password', {'created_at': reset_task.created_at,
                                        'is_processed': reset_task.is_processed}))

    return data


def collect_change_credentials_data(account_id):
    data = []

    for change_task in models.ChangeCredentialsTask.objects.filter(account=account_id):
        data.append(('change_credentials', {'created_at': change_task.created_at,
                                            'updated_at': change_task.updated_at,
                                            'state': change_task.state,
                                            'comment': change_task.comment,
                                            'old_email': change_task.old_email,
                                            'new_email': change_task.new_email,
                                            'new_nick': change_task.new_nick}))

    return data


def collect_full_data(account_id):
    data = []

    clans_data_protection.collect_account_data(account_id)

    data.extend(collect_account_data(account_id))
    data.extend(collect_might_data(account_id))
    data.extend(collect_reset_password_data(account_id))
    data.extend(collect_change_credentials_data(account_id))

    data.extend(friends_data_protection.collect_data(account_id))

    data.extend(third_party_data_protection.collect_data(account_id))

    data.extend(heroes_data_protection.collect_data(account_id))

    data.extend(bank_data_protection.collect_data(account_id))

    data.extend(xsolla_data_protection.collect_data(account_id))

    return [(name, postprocess_value(value)) for name, value in data]


def verbose(name):
    return {'the_tale': 'Сказка',
            'nick': 'ник',
            'description': 'описание',
            'last_news_remind_time': 'последнее напоминание о новостях',
            'gender': 'пол',
            'infinit_subscription': 'вечный подписчик',
            'subscription_end_at': 'окончание подписки',
            'subscription_expired_notification_send_at': 'выслано сообщение об окончании подписки',
            'active_end_at': 'время окончания статуса активности',
            'ban_game_end_at': 'время окончания бана в игре',
            'ban_forum_end_at': 'время окончания бана на форуме',
            'clan_id': 'идентификатор гильдии',
            'created_at': 'время создания',
            'updated_at': 'время последнего обновления',
            'email': 'email',
            'personal_messages_subscription': 'подписан на рассылку личных сообщений',
            'news_subscription': 'подписан на рассылку новостей',
            'referer_domain': 'домен, с которого пришёл в игру',
            'referer': 'страница, с которой пришёл в игру',
            'referral_of': 'реферал игрока',
            'referrals_number': 'привёл рефералов',
            'action_id': 'маркетиноговая акция, по которой пришёл в игру',
            'mights': 'могущество',
            'type': 'тип',
            'reset_password': 'сброс пароля',
            'is_processed': 'обработано',
            'change_credentials': 'изменение свойств аккаунта',
            'state': 'состояние',
            'comment': 'комментарий',
            'old_email': 'старый email',
            'new_email': 'новый email',
            'new_nick': 'новый ник',
            'friendship': 'запись о дружбе',
            'friend_1': 'идентификатор аккаунта 1',
            'friend_2': 'идентификатор аккаунта 2',
            'is_confirmed': 'подтверждено',
            'text': 'текст',
            'uid': 'уникальный идентификатор',
            'application_name': 'имя приложения',
            'application_info': 'инфрмация о приложении',
            'application_description': 'описание приложения',
            'hero:short_name': 'имя героя',
            'hero:long_name': 'все формы имени героя',
            'hero:description': 'описание героя',
            'game_invoice': 'платёж внутри игры',
            'recipient_id': 'идентификатор получателя',
            'recipient_type': 'тип получателя',
            'sender_id': 'идентификатор отправителя',
            'sender_type': 'тип отправителя',
            'amount': 'количество',
            'currency': 'валюта',
            'description_for_sender': 'описание для отправителя',
            'description_for_recipient': 'описание для получателя',
            'xsolla_invoice': 'платёж в XSolla',
            'id': 'идентификатор',
            'pay_result': 'результат платежа',
            'date': 'дата',
            'property:accept_invites_from_clans': 'согласен принимать приглашения в гильдии',
            'property:last_card_by_emissary': 'последнее время получения карты от эмиссара',
            'property:last_premium_by_emissary': 'последнее время плучения подписки от эмиссара',

            'tt_personal_messages': 'личные сообщения',
            'message': 'соообщение',
            'sender': 'отправитель',
            'removed': 'удалено',
            'recipients': 'получатели',

            'tt_discord': 'Discord (чат)',
            'discord_id': 'идентификатор в Discord',
            'code': 'код',
            'expire_at': 'время окончания действия',
            'bind_code': 'код связи аккаунтов игры и Discord',

            'tt_players_properties': 'Свойства аккаунта',
            'property': 'свойство',
            'value': 'значение'}.get(name, name)


#############
# remove data
#############

def remove_might_data(account_id):
    models.Award.objects.filter(account=account_id).delete()


def remove_reset_password_data(account_id):
    models.ResetPasswordTask.objects.filter(account=account_id).delete()


def remove_change_credentials_data(account_id):
    models.ChangeCredentialsTask.objects.filter(account=account_id).delete()


def remove_account_data(account_id):

    now = datetime.datetime.now()
    zero = datetime.datetime.fromtimestamp(0)

    arguments = dict(nick=logic.reset_nick_value(),
                     description='',
                     last_news_remind_time=zero,
                     gender=game_relations.GENDER.MALE,
                     premium_end_at=zero,
                     premium_expired_notification_send_at=zero,
                     permanent_purchases=s11n.to_json([]),
                     active_end_at=zero,
                     ban_game_end_at=zero,
                     ban_forum_end_at=zero,
                     updated_at=now,
                     email=None,
                     personal_messages_subscription=False,
                     news_subscription=False,
                     referer_domain=None,
                     referer=None,
                     referral_of_id=None,
                     referrals_number=0,
                     action_id=None,
                     might=0)

    models.Account.objects.filter(id=account_id).update(**arguments)


def remove_data(account_id):

    # must be first
    if not heroes_data_protection.remove_data(account_id):
        return False

    shop_data_protection.remove_data(account_id)

    # must be before remove_account_data
    clans_data_protection.remove_account_data(account_id)

    remove_account_data(account_id)

    remove_might_data(account_id)
    remove_reset_password_data(account_id)
    remove_change_credentials_data(account_id)

    friends_data_protection.remove_data(account_id)

    third_party_data_protection.remove_data(account_id)

    bank_data_protection.remove_data(account_id)
    xsolla_data_protection.remove_data(account_id)

    return True


def first_step_removing(account):
    tt_services.data_protector.cmd_request_deletion(ids=ids_list(account))

    new_password = utils_password.generate_password(len_=conf.settings.RESET_PASSWORD_LENGTH)
    new_password = django_auth_hashers.make_password(new_password)

    logic.change_credentials(account,
                             new_email=None,
                             new_password=new_password)

    removed_at = datetime.datetime.now()

    account._model.removed_at = removed_at
    models.Account.objects.filter(id=account.id).update(removed_at=removed_at)


def ids_list(account):
    return [('the_tale', account.id),
            ('tt_players_properties', account.id),
            ('tt_personal_messages', account.id),
            ('tt_discord', account.id)]
