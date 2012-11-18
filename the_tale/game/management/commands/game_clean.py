# coding: utf-8

from django.core.management.base import BaseCommand

from game.logic import clean_database


class Command(BaseCommand):

    help = 'clean database'

    def handle(self, *args, **options):

        clean_database()
