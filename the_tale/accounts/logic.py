# coding: utf-8
import urllib
import datetime

from django.conf import settings as project_settings
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout
from django.core.urlresolvers import reverse

from dext.utils.decorators import nested_commit_on_success

from accounts.models import Account
from accounts.prototypes import AccountPrototype
from accounts.exceptions  import AccountsException
from accounts.conf import accounts_settings

from game.heroes.prototypes import HeroPrototype
from game.bundles import BundlePrototype
from game.logic import dress_new_hero


class REGISTER_USER_RESULT:
    OK = 0
    DUPLICATE_USERNAME = 1
    DUPLICATE_EMAIL = 2


def login_url(target_url='/'):
    return reverse('accounts:auth:login') + '?next_url=' + urllib.quote(target_url)


def register_user(nick, email=None, password=None):

    from game.logic_storage import LogicStorage

    if User.objects.filter(username=nick).exists():
        return REGISTER_USER_RESULT.DUPLICATE_USERNAME, None, None

    if email and User.objects.filter(email=email).exists():
        return REGISTER_USER_RESULT.DUPLICATE_EMAIL, None, None

    if (email and not password) or (not email and password):
        raise AccountsException('email & password must be specified or not specified together')

    if password is None:
        password = accounts_settings.FAST_REGISTRATION_USER_PASSWORD

    user = User.objects.create_user(nick, email, password)

    account = AccountPrototype.create(user=user, nick=nick, email=email, is_fast=not (email and password))

    bundle = BundlePrototype.create()

    storage = LogicStorage()

    hero = HeroPrototype.create(account=account, bundle=bundle, storage=storage, is_fast=account.is_fast)
    dress_new_hero(hero)
    hero.save()

    return REGISTER_USER_RESULT.OK, account.id, bundle.id


def login_user(request, username=None, password=None):
    user = django_authenticate(username=username, password=password)

    if request.user.id != user.id:
        request.session.flush()

    django_login(request, user)


def force_login_user(request, user):

    if request.user.id != user.id:
        request.session.flush()

    user.backend = project_settings.AUTHENTICATION_BACKENDS[0]

    django_login(request, user)



def logout_user(request):
    django_logout(request)
    request.session.flush()


def remove_account(account):
    if account.can_be_removed():
        with nested_commit_on_success():
            bundle = BundlePrototype.get_by_account_id(account.id)
            user = account.user

            account.remove()
            bundle.remove()
            user.delete()


def block_expired_accounts():

    expired_before = datetime.datetime.now() - datetime.timedelta(seconds=accounts_settings.FAST_ACCOUNT_EXPIRED_TIME)

    for account_model in Account.objects.filter(is_fast=True, created_at__lt=expired_before):
        remove_account(AccountPrototype(account_model))
