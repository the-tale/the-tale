# coding: utf-8
from django.core.management.base import BaseCommand


from game.ratings.prototypes import RatingValuesPrototype, RatingPlacesPrototype


class Command(BaseCommand):

    help = 'recalculate ratings'

    def handle(self, *args, **options):

        print 'recalculate values'

        RatingValuesPrototype.recalculate()

        print 'recalculate places'

        RatingPlacesPrototype.recalculate()
