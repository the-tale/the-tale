
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'fill specified account with all available cards whitch are needed to tests'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-a', '--account', action='store', type=int, dest='account', help='account identifier')
        parser.add_argument('-n', '--number', action='store', type=int, dest='number', help='number of full generators')
        parser.add_argument('-s', '--storage', action='store', type=int, dest='storage', default=relations.STORAGE.FAST.value, help='storage id')

    def handle(self, *args, **options):

        cards_to_store = []

        for i in range(options['number']):
            for card_type in types.CARD.records:
                cards_to_store.append(card_type.effect.create_card(available_for_auction=random.choice((True, False)), type=card_type))

        logic.change_cards(owner_id=options['account'], operation_type='test-import', to_add=cards_to_store, storage=relations.STORAGE(options['storage']))
