
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'recalculate ratings'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        self.logger.info('recalculate values')

        prototypes.RatingValuesPrototype.recalculate()

        self.logger.info('recalculate places')

        prototypes.RatingPlacesPrototype.recalculate()
