# coding: utf-8

from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout

from accounts.prototypes import AccountPrototype
from accounts.exceptions import AccountsException

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

    user = User.objects.create_user(nick, email, password)
    account = AccountPrototype.create(user=user)
    angel = AngelPrototype.create(account=account, name=user.username)
    hero = HeroPrototype.create(angel=angel)

    dress_new_hero(hero)

    hero.save()

    bundle = BundlePrototype.create(angel)

    return REGISTER_USER_RESULT.OK, account.id, bundle.id


def login_user(request, username=None, password=None, user=None):
    if username and password:
        user = django_authenticate(username=username, password=password)

    if not user:
        raise AccountsException('neither username and password or user must be specofied')

    request.session.flush()
    django_login(request, user)


def logout_user(request):
    django_logout(request)
    request.session.flush()
