# coding: utf-8
import random
import datetime

from django.dispatch import receiver

from dext.settings import settings

from the_tale.amqp_environment import environment

from the_tale.portal import signals as portal_signals
from the_tale.portal.conf import portal_settings

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.personal_messages.prototypes import MessagePrototype
from the_tale.accounts.logic import get_system_user


@receiver(portal_signals.day_started, dispatch_uid='portal_day_started')
def portal_day_started(sender, **kwargs): # pylint: disable=W0613
    accounts_query = AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now(),
                                                          ban_game_end_at__lt=datetime.datetime.now(),
                                                          ban_forum_end_at__lt=datetime.datetime.now(),
                                                          premium_end_at__lt=datetime.datetime.now())

    accounts_number = accounts_query.count()
    if accounts_number < 1:
        return

    account_model = accounts_query[random.randint(0, accounts_number-1)]

    account = AccountPrototype(model=account_model)

    settings[portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY] = str(account.id)

    environment.workers.accounts_manager.cmd_run_account_method(account_id=account.id,
                                                                         method_name=AccountPrototype.prolong_premium.__name__,
                                                                         data={'days': portal_settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY})

    message = u'''
Поздравляем!

Ваш герой выбран героем дня и Вы получаете %(days)d дней подписки!
''' % {'days': portal_settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY}

    MessagePrototype.create(get_system_user(), account, message)
