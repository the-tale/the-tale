# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.accounts.personal_messages.prototypes import MessagePrototype


class Command(BaseCommand):

    help = 'Remove old messages from system_user'

    requires_model_validation = False

    def handle(self, *args, **options):
        MessagePrototype.remove_old_messages()
