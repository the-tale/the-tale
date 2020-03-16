
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'create super user'

    LOCKS = ['game_commands', 'portal_commands']

    GAME_MUST_BE_STOPPED = True

    def _handle(self, *args, **options):
        if models.Account.objects.exists():
            self.logger.info('some users have created already, superuser MUST be created first')
            exit(0)

        NICK = 'superuser'
        EMAIL = 'superuser@example.com'
        PASSWORD = '111111'

        result, account_id, bundle_id = logic.register_user(NICK,
                                                            email=EMAIL,
                                                            password=PASSWORD,
                                                            referer=None,
                                                            referral_of_id=None,
                                                            action_id=None,
                                                            is_bot=False,
                                                            full_create=False)

        models.Account.objects.filter(id=account_id).update(is_superuser=True, is_staff=True)

        self.logger.info(f'nick: {NICK}')
        self.logger.info(f'email {EMAIL}')
        self.logger.info(f'password {PASSWORD}')
        self.logger.info('login to site.url/admin and change password!')
