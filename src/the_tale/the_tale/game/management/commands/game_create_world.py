# coding: utf-8

from django.core.management.base import BaseCommand


from the_tale.game import logic


class Command(BaseCommand):

    help = 'create new worldd'

    def handle(self, *args, **options):
        logic.create_test_map()
