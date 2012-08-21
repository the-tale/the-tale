# coding: utf-8

from django.core.management.base import BaseCommand

from textgen import words
from dext.utils import s11n

from game.map.places.storage import places_storage

class Command(BaseCommand):

    help = 'fill name forms'

    requires_model_validation = False

    def handle(self, *args, **options):

        for place in places_storage.all():
            if not place.model.name_forms:
                forms = [place.name] * 12
                if ' ' in place.name:
                    place.model.name_forms = s11n.to_json(words.NounGroup(place.name, forms=forms).serialize())
                else:
                    place.model.name_forms = s11n.to_json(words.Noun(place.name, forms=forms).serialize())

            place.save()
