
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Send test message to sentry'

    LOCKS = []

    requires_model_validation = False

    GAME_CAN_BE_IN_MAINTENANCE_MODE = True

    def _handle(self, *args, **options):
        if django_settings.SENTRY_RAVEN_CONFIG:
            sentry_sdk.capture_message(f'Test message {datetime.datetime.utcnow().isoformat()}')
            self.logger.info('Test message sent.')
        else:
            self.logger.info('Sentry did not configured. Can not send test message.')
