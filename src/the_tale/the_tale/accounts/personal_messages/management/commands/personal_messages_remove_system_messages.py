
from django.core.management.base import BaseCommand

from the_tale.accounts.personal_messages import tt_api


class Command(BaseCommand):

    help = 'Remove old messages from system_user'

    requires_model_validation = False

    def handle(self, *args, **options):
        tt_api.remove_old_system_messages()
