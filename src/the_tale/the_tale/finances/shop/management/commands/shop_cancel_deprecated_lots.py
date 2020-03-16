
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    LOCKS = ['portal_commands']

    help = 'cancel all market lots, that moved out of game'

    def _handle(self, *args, **options):

        info = tt_services.market.cmd_info()
        cards_info = cards_logic.get_cards_info_by_full_types()

        for record in info:
            self.logger.info(f'check "{record.full_type}"')

            if record.full_type in cards_info:
                continue

            self.logger.info(f'type "{record.full_type}" does not found between card types, close it\'s lots')

            lots = logic.cancel_lots_by_type(item_type=record.full_type)

            self.logger.info(f'lots canceled: {len(lots)}')
