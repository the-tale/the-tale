# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.accounts.achievements import models
from the_tale.accounts.achievements import storage
from the_tale.accounts.achievements import prototypes

from the_tale.collections.prototypes import AccountItemsPrototype, GiveItemTaskPrototype



class Command(BaseCommand):

    help = 'Recalculate mights of accounts'

    def handle(self, *args, **options):

        for achievements in models.AccountAchievements.objects.all().iterator():
            prototype = prototypes.AccountAchievementsPrototype(achievements)

            collection = AccountItemsPrototype.get_by_account_id(prototype.account_id)

            for achievement_id in prototype.achievements.achievements_ids():
                for item in storage.achievements_storage[achievement_id].rewards:
                    if not collection.has_item(item):
                        GiveItemTaskPrototype.create(prototype.account_id, item.id)
