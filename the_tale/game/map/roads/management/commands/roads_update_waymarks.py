# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):
        from ...logic import update_waymarks
        update_waymarks()
