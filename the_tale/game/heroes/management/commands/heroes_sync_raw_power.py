# coding: utf-8
from django.core.management.base import BaseCommand


from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.prototypes import HeroPrototype


class Command(BaseCommand):

    help = 'sync heroes raw power'

    def handle(self, *args, **options):

        for hero_model in Hero.objects.all():
            hero = HeroPrototype(hero_model)
            hero.model.raw_power = hero.power
            hero.save()
