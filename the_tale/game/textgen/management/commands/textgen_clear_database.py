# coding: utf-8
from django.core.management.base import BaseCommand

from ...templates import Vocabulary, Dictionary

class Command(BaseCommand):

    help = 'load texts into databse'

    def handle(self, *args, **options):

        vocabulary = Vocabulary()
        vocabulary.clear()

        dictionary = Dictionary()
        dictionary.clear()

