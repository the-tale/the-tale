# coding: utf-8

from django.contrib.auth.models import User

from dext.utils.decorators import nested_commit_on_success

from accounts.prototypes import AccountPrototype

from game.angels.prototypes import AngelPrototype
from game.heroes.prototypes import HeroPrototype
from game.bundles import BundlePrototype
from game.logic import dress_new_hero


class REGISTER_USER_RESULT:
    OK = 0
    DUPLICATE_USERNAME = 1
    DUPLICATE_EMAIL = 2


@nested_commit_on_success
def register_user(nick, email, password):

    if User.objects.filter(username=nick).exists():
        return REGISTER_USER_RESULT.DUPLICATE_USERNAME, None

    if User.objects.filter(email=email).exists():
        return REGISTER_USER_RESULT.DUPLICATE_EMAIL, None

    user = User.objects.create_user(nick, email, password)

    account = AccountPrototype.create(user=user)
    angel = AngelPrototype.create(account=account, name=user.username)
    hero = HeroPrototype.create(angel=angel)

    dress_new_hero(hero)

    hero.save()

    bundle = BundlePrototype.create(angel)

    return REGISTER_USER_RESULT.OK, bundle.id
