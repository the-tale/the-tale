# coding: utf-8
import datetime

from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout

from dext.utils.decorators import nested_commit_on_success

from accounts.models import Account
from accounts.prototypes import AccountPrototype
from accounts.exceptions  import AccountsException
from accounts.conf import accounts_settings

from game.angels.prototypes import AngelPrototype
from game.heroes.prototypes import HeroPrototype
from game.bundles import BundlePrototype
from game.logic import dress_new_hero


class REGISTER_USER_RESULT:
    OK = 0
    DUPLICATE_USERNAME = 1
    DUPLICATE_EMAIL = 2


def register_user(nick, email=None, password=None):

    if User.objects.filter(username=nick).exists():
        return REGISTER_USER_RESULT.DUPLICATE_USERNAME, None, None

    if email and User.objects.filter(email=email).exists():
        return REGISTER_USER_RESULT.DUPLICATE_EMAIL, None, None

    if (email and not password) or (not email and password):
        raise AccountsException('email & password must be specified or not specified together')

    if password is None:
        password = accounts_settings.FAST_REGISTRATION_USER_PASSWORD

    user = User.objects.create_user(nick, email, password)
    account = AccountPrototype.create(user=user, is_fast=not (email and password))
    angel = AngelPrototype.create(account=account, name=user.username)
    hero = HeroPrototype.create(angel=angel)

    dress_new_hero(hero)

    hero.save()

    bundle = BundlePrototype.create(angel)

    return REGISTER_USER_RESULT.OK, account.id, bundle.id


def login_user(request, username=None, password=None):
    request.session.flush()
    user = django_authenticate(username=username, password=password)
    django_login(request, user)


def logout_user(request):
    django_logout(request)
    request.session.flush()


def block_expired_accounts():

    expired_before = datetime.datetime.now() - datetime.timedelta(seconds=accounts_settings.FAST_ACCOUNT_EXPIRED_TIME)

    for account_model in Account.objects.filter(is_fast=True, created_at__lt=expired_before):
        account = AccountPrototype(account_model)
        if account.can_be_removed():
            with nested_commit_on_success():
                bundle = BundlePrototype.get_by_angel(account.angel)
                user = account.user

                account.remove()
                bundle.remove()
                user.delete()
