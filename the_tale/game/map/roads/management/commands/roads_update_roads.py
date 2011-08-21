# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ...logic import update_roads

class Command(BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):

        update_roads()
