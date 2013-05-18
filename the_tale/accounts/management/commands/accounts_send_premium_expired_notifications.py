# coding: utf-8

from django.core.management.base import BaseCommand

from accounts.prototypes import AccountPrototype

class Command(BaseCommand):

    help = 'send premium expired notifications'

    requires_model_validation = False

    def handle(self, *args, **options):
        AccountPrototype.send_premium_expired_notifications()
