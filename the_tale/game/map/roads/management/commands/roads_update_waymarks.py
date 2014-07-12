# coding: utf-8
from django.core.management.base import BaseCommand

from the_tale.game.map.roads.logic import update_waymarks


class Command(BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):
        update_waymarks()
