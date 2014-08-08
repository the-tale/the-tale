# coding: utf-8
import datetime

from django.conf import settings as project_settings
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout
from django.db import transaction

from dext.common.utils.logic import normalize_email
from dext.common.utils.urls import url

from the_tale.common.utils.password import generate_password

from the_tale.accounts.models import Account
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import exceptions
from the_tale.accounts.conf import accounts_settings

from the_tale.accounts.achievements.prototypes import AccountAchievementsPrototype
from the_tale.collections.prototypes import AccountItemsPrototype

from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.bundles import BundlePrototype
from the_tale.game.logic import dress_new_hero, messages_for_new_hero


class REGISTER_USER_RESULT:
    OK = 0
    DUPLICATE_USERNAME = 1
    DUPLICATE_EMAIL = 2


def login_url(target_url='/'):
    return url('accounts:auth:api-login', api_version='1.0', api_client=project_settings.API_CLIENT, next_url=target_url.encode('utf-8'))

def login_page_url(target_url='/'):
    return url('accounts:auth:page-login', next_url=target_url.encode('utf-8'))

def logout_url():
    return url('accounts:auth:api-logout', api_version='1.0', api_client=project_settings.API_CLIENT)


def get_system_user():
    account = AccountPrototype.get_by_nick(accounts_settings.SYSTEM_USER_NICK)
    if account: return account

    register_result, account_id, bundle_id = register_user(accounts_settings.SYSTEM_USER_NICK, # pylint: disable=W0612
                                                           email=project_settings.EMAIL_NOREPLY,
                                                           password=generate_password(len_=accounts_settings.RESET_PASSWORD_LENGTH))

    account = AccountPrototype.get_by_id(account_id)
    account._model.active_end_at = datetime.datetime.fromtimestamp(0)
    account.save()

    return account


def register_user(nick, email=None, password=None, referer=None, referral_of_id=None, action_id=None, is_bot=False):

    if Account.objects.filter(nick=nick).exists():
        return REGISTER_USER_RESULT.DUPLICATE_USERNAME, None, None

    if email and Account.objects.filter(email=email).exists():
        return REGISTER_USER_RESULT.DUPLICATE_EMAIL, None, None

    try:
        referral_of = AccountPrototype.get_by_id(referral_of_id)
    except ValueError:
        referral_of = None

    if (email and not password) or (not email and password):
        raise exceptions.EmailAndPasswordError()

    is_fast = not (email and password)

    if is_fast and is_bot:
        raise exceptions.BotIsFastError()

    if password is None:
        password = accounts_settings.FAST_REGISTRATION_USER_PASSWORD

    account = AccountPrototype.create(nick=nick,
                                      email=email,
                                      is_fast=is_fast,
                                      is_bot=is_bot,
                                      password=password,
                                      referer=referer,
                                      referral_of=referral_of,
                                      action_id=action_id)

    AccountAchievementsPrototype.create(account)
    AccountItemsPrototype.create(account)

    bundle = BundlePrototype.create()

    hero = HeroPrototype.create(account=account, bundle=bundle)
    dress_new_hero(hero)
    messages_for_new_hero(hero)
    hero.save()

    return REGISTER_USER_RESULT.OK, account.id, bundle.id


def login_user(request, nick=None, password=None, remember=False):
    user = django_authenticate(nick=nick, password=password)

    if request.user.id != user.id:
        request.session.flush()

    django_login(request, user)

    if remember:
        request.session.set_expiry(accounts_settings.SESSION_REMEMBER_TIME)


def force_login_user(request, user):

    if request.user.id != user.id:
        request.session.flush()

    user.backend = project_settings.AUTHENTICATION_BACKENDS[0]

    django_login(request, user)



def logout_user(request):
    django_logout(request)
    request.session.flush()


def remove_account(account):
    from the_tale.game.logic import remove_game_data
    if account.can_be_removed():
        with transaction.atomic():
            remove_game_data(account)
            account.remove()


def block_expired_accounts():

    expired_before = datetime.datetime.now() - datetime.timedelta(seconds=accounts_settings.FAST_ACCOUNT_EXPIRED_TIME)

    for account_model in Account.objects.filter(is_fast=True, created_at__lt=expired_before):
        remove_account(AccountPrototype(account_model))

# for bank
def get_account_id_by_email(email):
    account = AccountPrototype.get_by_email(normalize_email(email))
    return account.id if account else None
