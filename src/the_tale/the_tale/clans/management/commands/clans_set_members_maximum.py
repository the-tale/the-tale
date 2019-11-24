
import smart_imports

smart_imports.all()

clans = {399: 45,
         313: 45,
         13: 45,
         57: 44,
         5: 42,
         85: 29,
         666: 27,
         613: 27,
         23: 26,
         29: 25,
         164: 25,
         31: 18,
         763: 17,
         4: 16,
         106: 12,
         555: 11,
         25: 10,
         78: 10,
         42: 7,
         59: 7,
         16: 7,
         64: 7,
         87: 6,
         143: 5,
         365: 5,
         770: 4,
         50: 2,
         62: 2,
         537: 2,
         43: 1,
         24: 1,
         21: 1,
         48: 1}


class Command(django_management.BaseCommand):

    help = 'set initial maximum_members attribute'

    def handle(self, *args, **options):
        for clan_id, level in clans.items():
            tt_services.properties.cmd_set_property(clan_id,
                                                    relations.UPGRADABLE_PROPERTIES.MEMBERS_MAXIMUM.property,
                                                    level)
