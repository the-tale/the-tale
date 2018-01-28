
from django.core.management.base import BaseCommand

from the_tale.game import tt_api as game_tt_api
from the_tale.game.heroes import models


class Command(BaseCommand):

    help = 'migrate energy to separate service'

    def handle(self, *args, **options):

        for hero in models.Hero.objects.all().order_by('id').iterator():
            print('process hero {}'.format(hero.id))
            game_tt_api.change_energy_balance(account_id=hero.account_id,
                                              type='initial_import',
                                              energy=hero.energy + hero.energy_bonus,
                                              async=False,
                                              autocommit=True)
