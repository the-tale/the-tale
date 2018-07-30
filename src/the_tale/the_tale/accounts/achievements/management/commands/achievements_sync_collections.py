
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Recalculate mights of accounts'

    def handle(self, *args, **options):

        for achievements in models.AccountAchievements.objects.all().iterator():
            prototype = prototypes.AccountAchievementsPrototype(achievements)

            collection = collections_prototypes.AccountItemsPrototype.get_by_account_id(prototype.account_id)

            for achievement_id in prototype.achievements.achievements_ids():
                for item in storage.achievements[achievement_id].rewards:
                    if not collection.has_item(item):
                        collections_prototypes.GiveItemTaskPrototype.create(prototype.account_id, item.id)
