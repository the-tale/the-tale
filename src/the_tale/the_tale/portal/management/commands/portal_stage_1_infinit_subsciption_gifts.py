
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'gift infinit subscription to all payers and users with might > 100'

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

        # gift infinit subscription

        for i, account_id in enumerate(ids):
            self.logger.info(f'process account {account_id} [{i}/{len(ids)}]')

            account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

            if shop_price_list.stage_1_inifinit_subscription_gift.purchase_type in account.permanent_purchases:
                self.logger.info(f'skip account {account_id} [{i}/{len(ids)}]')
                continue

            shop_price_list.stage_1_inifinit_subscription_gift.buy(account=account)

        self.logger.info('process completed')
