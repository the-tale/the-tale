
import smart_imports

smart_imports.all()


class FakeEffect(effects.BaseEffect):
    pass


class ALL_CARDS(types.CARD):
    records = (('REPAIR_BUILDING_UNCOMMON', 57, 'волшебный инструмен', types.FOR_PREMIUMS, types.UNCOMMON, FakeEffect(), []),
               ('REPAIR_BUILDING_COMMON', 134, 'должок мастеровых', types.FOR_PREMIUMS, types.COMMON, FakeEffect(), []),
               ('REPAIR_BUILDING_RARE', 135, 'домовой', types.FOR_PREMIUMS, types.RARE, FakeEffect(), []),)


def constructor(type, **kwargs):

    def real_constructor(removed_card):
        return type.effect.create_card(type,
                                       available_for_auction=removed_card.available_for_auction,
                                       **kwargs)

    return real_constructor


CONSTRUCTORS_MAP = {
    '57': constructor(type=types.CARD.ADD_PLACE_POWER_UNCOMMON, direction=1),
    '134': constructor(type=types.CARD.ADD_PLACE_POWER_COMMON, direction=1),
    '135': constructor(type=types.CARD.ADD_PLACE_POWER_RARE, direction=1)
    }


class DepreactedStorageClient(tt_services.StorageClient):

    def protobuf_to_item(self, pb_item):
        return super().protobuf_to_item(pb_item=pb_item,
                                        cards=ALL_CARDS)


depreacted_storage = DepreactedStorageClient(entry_point=conf.settings.TT_STORAGE_ENTRY_POINT)


class Command(django_management.BaseCommand):

    help = 'replace old cards by new (for all players)'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):

        accounts_ids = accounts_models.Account.objects.values_list('id', flat=True)

        accounts_number = len(accounts_ids)

        total_replaced = 0

        for i, account_id in enumerate(accounts_ids):
            print('process {} / {}'.format(i, accounts_number))

            cards = depreacted_storage.cmd_get_items(account_id)

            removed_cards = []
            added_cards = []

            for card in cards.values():
                if card.item_full_type not in CONSTRUCTORS_MAP:
                    continue

                removed_cards.append(card)
                added_cards.append(CONSTRUCTORS_MAP[card.item_full_type](removed_card=card))

            if not removed_cards:
                continue

            logic.change_cards(owner_id=account_id,
                               operation_type='#replace_deprecated_cards',
                               to_add=added_cards,
                               to_remove=removed_cards,
                               storage=relations.STORAGE.NEW)

            print('replaced: ', len(added_cards))

            total_replaced += len(added_cards)

        print('total replaced: ', total_replaced)
