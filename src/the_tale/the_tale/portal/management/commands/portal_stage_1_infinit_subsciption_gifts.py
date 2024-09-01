
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'gift money to all payers and users with might > 100 or who made a purchase'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        # mights filter
        might_ids = accounts_prototypes.AccountPrototype.live_query().filter(might__gte=100).values_list('id', flat=True)

        # purchase filter

        bank_ids = bank_models.Invoice.objects.filter(state=bank_relations.INVOICE_STATE.CONFIRMED,
                                                      recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                      sender_type=bank_relations.ENTITY_TYPE.XSOLLA).values_list('recipient_id', flat=True)

        ids = list(sorted(set(might_ids) | set(bank_ids)))

        self.logger.info(f'found {len(ids)} accounts')

        # gift money

        game_master = accounts_prototypes.AccountPrototype.get_by_id(1)

        for i, account_id in enumerate(ids):
            self.logger.info(f'process account {account_id} [{i}/{len(ids)}]')

            account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

            shop_logic.transaction_gm(account=account,
                                      amount=1500,
                                      description="Подарок от разработчиков, чтобы весело проводить Сказку.",
                                      game_master=game_master)

        self.logger.info('process completed')
