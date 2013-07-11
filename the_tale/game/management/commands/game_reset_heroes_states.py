# coding: utf-8

from django.core.management.base import BaseCommand

from game.map.places.storage import places_storage

from game.heroes.prototypes import HeroPrototype
from game.quests.prototypes import QuestPrototype

class Command(BaseCommand):

    help = 'reset heroes state (position, actions, quests)'

    requires_model_validation = False

    def handle(self, *args, **options):

        for i, hero_id in enumerate(HeroPrototype._model_class.objects.all().values_list('id', flat=True)):
            print i
            hero = HeroPrototype.get_by_id(hero_id)
            hero.actions.reset_to_idl()
            hero.position.set_place(places_storage.random_place())
            hero.bag = '{}' # remove all bag (threre can be quest items)
            hero.save()

        QuestPrototype._model_class.objects.all().delete()
