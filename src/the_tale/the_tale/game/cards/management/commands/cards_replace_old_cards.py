
import smart_imports

smart_imports.all()


class FakeEffect(effects.BaseEffect):
    pass


class ALL_CARDS(types.CARD):
    records = (('ADD_BONUS_ENERGY_COMMON', 5, 'капля энергии', types.FOR_ALL, types.COMMON, FakeEffect(), []),
               ('ADD_BONUS_ENERGY_UNCOMMON', 6, 'чаша Силы', types.FOR_ALL, types.UNCOMMON, FakeEffect(), []),
               ('ADD_BONUS_ENERGY_RARE', 7, 'магический вихрь', types.FOR_ALL, types.RARE, FakeEffect(), []),
               ('ADD_BONUS_ENERGY_EPIC', 8, 'энергетический шторм', types.FOR_ALL, types.EPIC, FakeEffect(), []),
               ('ADD_BONUS_ENERGY_LEGENDARY', 9, 'шквал Силы', types.FOR_ALL, types.LEGENDARY, FakeEffect(), []))


def constructor(type, **kwargs):

    def real_constructor(removed_card):
        return type.effect.create_card(type,
                                       available_for_auction=removed_card.available_for_auction,
                                       **kwargs)

    return real_constructor


CONSTRUCTORS_MAP = {
    '5': constructor(type=types.CARD.REGENERATION),
    '6': constructor(type=types.CARD.LONG_TELEPORT),
    '7': constructor(type=types.CARD.HEAL_COMPANION_RARE),
    '8': constructor(type=types.CARD.HEAL_COMPANION_EPIC),
    '9': constructor(type=types.CARD.ADD_GOLD_LEGENDARY)}


class DepreactedStorageClient(tt_services.StorageClient):

    def protobuf_to_item(self, pb_item):
        return super().protobuf_to_item(pb_item=pb_item,
                                        cards=ALL_CARDS)


depreacted_storage = DepreactedStorageClient(entry_point=conf.settings.TT_STORAGE_ENTRY_POINT)


class Command(utilities_base.Command):

    help = 'replace old cards by new (for all players)'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        accounts_ids = accounts_models.Account.objects.values_list('id', flat=True)

        accounts_number = len(accounts_ids)

        total_replaced = 0

        for i, account_id in enumerate(accounts_ids):
            self.logger.info('process {} / {}'.format(i, accounts_number))

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

            self.logger.info(f'replaced: {len(added_cards)}')

            total_replaced += len(added_cards)

        self.logger.info(f'total replaced: {total_replaced}')
