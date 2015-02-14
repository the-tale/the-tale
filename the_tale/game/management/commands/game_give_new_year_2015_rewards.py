# coding: utf-8
import datetime

from django.core.management.base import BaseCommand

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.ratings import models as ratings_models

from the_tale.game.companions import storage as companions_storage
from the_tale.game.cards import effects as cards_effects

from the_tale.market import goods_types

goods_types.autodiscover()


class Command(BaseCommand):

    help = 'give rewards for 2014-2015 new year event'

    requires_model_validation = False


    def handle(self, *args, **options):

        CARDS = [companions_storage.companions[5],
                 companions_storage.companions[4],
                 companions_storage.companions[3],
                 companions_storage.companions[1],
                 companions_storage.companions[2]]

        accounts = list(ratings_models.RatingValues.objects.filter(gifts_returned__gt=0).order_by('-gifts_returned').values_list('account_id', 'gifts_returned'))

        print 'total accounts: ', len(accounts)

        delta = len(accounts) / 5

        groups = []

        for i in xrange(5):
            group = accounts[:delta]
            accounts = accounts[delta:]

            while accounts and group[-1][1] == accounts[0][-1]:
                group.append(accounts[0])
                accounts.pop(0)

            groups.append(group)

        for i, (group, companion) in enumerate(zip(groups, CARDS)):
            print 'process group %d [%d accounts]' % (i, len(group))
            print u'give companion «%s»' % companion.name
            for account_id, gifts in group:
                hero = HeroPrototype.get_by_account_id(account_id)

                is_premium = hero.premium_state_end_at > datetime.datetime.now()

                hero.cards.add_card(cards_effects.GetCompanionLegendary().create_card(available_for_auction=is_premium, companion=companion))
                hero.save()
