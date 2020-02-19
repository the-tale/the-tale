
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'cancel all market lots, that moved out of game'

    def handle(self, *args, **options):

        info = tt_services.market.cmd_info()
        cards_info = cards_logic.get_cards_info_by_full_types()

        for record in info:
            print(f'check "{record.full_type}"')

            if record.full_type in cards_info:
                continue

            print(f'type "{record.full_type}" does not found between card types, close it\'s lots')

            lots = logic.cancel_lots_by_type(item_type=record.full_type)

            print(f'lots canceled: {len(lots)}')
