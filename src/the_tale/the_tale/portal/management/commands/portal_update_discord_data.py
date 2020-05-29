
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    LOCKS = ['portal_commands']

    help = 'force refresh all discord bot account data'

    def _handle(self, *args, **options):

        query = accounts_models.Account.objects.filter(is_fast=False).order_by('id')

        accounts_number = query.count()

        for i, account_model in enumerate(query.iterator()):
            self.logger.info('Sync account %s to discord [%s/%s] — %s%%',
                             account_model.id,
                             i,
                             accounts_number,
                             round(i / accounts_number * 100, 2))

            discord_user = discord.construc_user_info(accounts_prototypes.AccountPrototype(model=account_model))

            tt_services.discord.cmd_update_user(user=discord_user, force=True)
