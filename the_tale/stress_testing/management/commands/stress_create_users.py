# -*- coding: utf-8 -*-
import random
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    help = 'update map on base of current database state'

    option_list = BaseCommand.option_list + ( make_option('-A', '--accouns-number',
                                                          action='store',
                                                          type=int,
                                                          default=1,
                                                          dest='accouns_number',
                                                          help='number of created accounts'),
                                              make_option('-H', '--heroes-number',
                                                          action='store',
                                                          type=int,
                                                          default=1,
                                                          dest='heroes_number',
                                                          help='number of created heroes per account'),
                                              make_option('-P', '--nick-preffix',
                                                          action='store',
                                                          type=str,
                                                          dest='nick_preffix',
                                                          help='preffix for user nicks'),
                                              )

    def handle(self, *args, **options):

        from accounts.prototypes import AccountPrototype
        from game.angels.prototypes import AngelPrototype
        from game.heroes.prototypes import HeroPrototype

        accouns_number = options['accouns_number']
        heroes_number = options['heroes_number']
        nick_preffix = options['nick_preffix']

        for account_number in xrange(accouns_number):

            nick = 'stress_account_%s_%d' % (nick_preffix, account_number)

            user = User.objects.create_user(nick, '%s@nick.com' % nick, '111111')
            account = AccountPrototype.create(user=user)
            angel = AngelPrototype.create(account=account, name=user.username)

            for hero_number in xrange(heroes_number):
                name = 'stress_hero_%d_%d' % (account_number, hero_number)
                HeroPrototype.create(angel, 
                                     name,
                                     first=True,
                                     intellect=random.randint(1, 5),
                                     constitution=random.randint(1, 5),
                                     reflexes=random.randint(1, 5),
                                     chaoticity=random.randint(1, 5), 
                                     charisma=random.randint(1, 5), 
                                     npc=False)
            
