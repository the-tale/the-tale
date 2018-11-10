
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'recalculate ratings'

    def handle(self, *args, **options):

        print('recalculate values')

        prototypes.RatingValuesPrototype.recalculate()

        print('recalculate places')

        prototypes.RatingPlacesPrototype.recalculate()
