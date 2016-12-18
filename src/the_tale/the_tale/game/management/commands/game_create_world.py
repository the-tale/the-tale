# coding: utf-8

from django.core.management.base import BaseCommand

from dext.common.utils.logic import run_django_command

from the_tale.game import logic
from the_tale.game.places import storage as places_storage


class Command(BaseCommand):

    help = 'create new world'

    def handle(self, *args, **options):
        if len(places_storage.places.all()) != 0:
            return

        logic.create_test_map()

        run_django_command(['map_update_map'])
