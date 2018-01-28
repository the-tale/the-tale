
import datetime

from django.core.management.base import BaseCommand

from the_tale.game.cards import logic as cards_logic
from the_tale.game.cards import tt_api as cards_tt_api
from the_tale.game.cards import relations as cards_relations

from the_tale.game.heroes import models


class Command(BaseCommand):

    help = 'migrate cards points to cards'

    def handle(self, *args, **options):

        HELP_COUNTS_TO_NEW_CARD = 9

        for hero in models.Hero.objects.all().order_by('id').iterator():
            print('process hero {}'.format(hero.id))

            cards = hero.data.get('cards', {})

            help_count = cards.get('help_count', 0)
            premium_help_count = cards.get('premium_help_count', 0)

            non_tradable_cards = (help_count - premium_help_count) // HELP_COUNTS_TO_NEW_CARD

            if (help_count - premium_help_count) % HELP_COUNTS_TO_NEW_CARD:
                non_tradable_cards += 1

            tradable_cards = premium_help_count // HELP_COUNTS_TO_NEW_CARD

            if premium_help_count % HELP_COUNTS_TO_NEW_CARD:
                tradable_cards += 1

            energy = hero.energy + hero.energy_bonus

            if hero.premium_state_end_at < datetime.datetime.utcnow():
                non_tradable_cards += energy // (4 * 9)
            else:
                tradable_cards += energy // (4 * 9)

            cards = []

            for i in range(non_tradable_cards):
                cards.append(cards_logic.create_card(allow_premium_cards=False, available_for_auction=False))

            for i in range(tradable_cards):
                cards.append(cards_logic.create_card(allow_premium_cards=True, available_for_auction=True))

            cards_tt_api.change_cards(account_id=hero.account_id,
                                      operation_type='migrate-to-tt-bank',
                                      storage=cards_relations.STORAGE.NEW,
                                      to_add=cards)

            print('hero received {} premium cards and {} non-premium'.format(tradable_cards, non_tradable_cards))
