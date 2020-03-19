
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Remove old messages from system_user'

    LOCKS = ['portal_commands']

    requires_model_validation = False

    def _handle(self, *args, **options):
        tt_services.personal_messages.cmd_remove_old_system_messages(accounts_logic.get_system_user_id(),
                                                                     conf.settings.SYSTEM_MESSAGES_LEAVE_TIME)
