#coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.game.places import nearest_cells


class Command(BaseCommand):

    help = 'for each place calculate nearest map cells'

    def handle(self, *args, **options):

        nearest_cells.update_nearest_cells()
