# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.accounts.third_party import logic

class Command(BaseCommand):

    help = 'remove expired acces tokens'

    requires_model_validation = False

    def handle(self, *args, **options):
        logic.remove_expired_access_tokens()
