# coding: utf-8

from optparse import make_option

from django.core.management.base import BaseCommand

from textgen.words import Noun

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.conf import accounts_settings

from the_tale.game.heroes.prototypes import HeroPrototype


class Command(BaseCommand):

    help = 'Create bot account'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-n', '--number',
                                                          action='store',
                                                          type=int,
                                                          dest='bots_number',
                                                          default=1,
                                                          help='howe many bots must be created'), )


    def handle(self, *args, **options):

        bots_number = options['bots_number']

        start_number = AccountPrototype._model_class.objects.filter(is_bot=True).count()

        for bot_number in xrange(start_number, start_number+bots_number):
            print 'creat bot #%d' % bots_number
            result, account_id, bundle_id = register_user(nick=accounts_settings.BOT_NICK_TEMPLATE % bot_number,
                                                          email=accounts_settings.BOT_EMAIL_TEMPLATE % bot_number,
                                                          password=accounts_settings.BOT_PASSWORD,
                                                          is_bot=True)
            bot_hero = HeroPrototype.get_by_account_id(account_id)

            bot_hero.set_normalized_name(Noun(normalized=accounts_settings.BOT_HERO_NAME_FORMS[0],
                                              forms=accounts_settings.BOT_HERO_NAME_FORMS,
                                              properties=accounts_settings.BOT_HERO_NAME_PROPERTIES))
            bot_hero.save()
