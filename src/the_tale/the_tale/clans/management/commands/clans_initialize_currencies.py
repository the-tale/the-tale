

import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'give points to clans'

    def handle(self, *args, **options):

        for clan_id in models.Clan.objects.all().values_list('id', flat=True):
            tt_services.currencies.cmd_change_balance(account_id=clan_id,
                                                      type='initial',
                                                      amount=tt_clans_constants.INITIAL_POINTS,
                                                      async=False,
                                                      autocommit=True,
                                                      currency=relations.CURRENCY.ACTION_POINTS)

            tt_services.currencies.cmd_change_balance(account_id=clan_id,
                                                      type='initial',
                                                      amount=tt_clans_constants.INITIAL_FREE_QUESTS,
                                                      async=False,
                                                      autocommit=True,
                                                      currency=relations.CURRENCY.FREE_QUESTS)
