
import smart_imports

smart_imports.all()


class FakeEffect(effects.BaseEffect):
    pass


class ALL_CARDS(types.CARD):
    records = (('MOST_COMMON_PLACES_UNCOMMON', 70, 'ошибка в архивах', types.FOR_ALL, types.UNCOMMON, FakeEffect(), []),
               ('MOST_COMMON_PLACES_RARE', 71, 'фальшивые рекомендации', types.FOR_ALL, types.RARE, FakeEffect(), []),
               ('MOST_COMMON_PLACES_EPIC', 72, 'застолье в Совете', types.FOR_ALL, types.EPIC, FakeEffect(), []),
               ('MOST_COMMON_PLACES_LEGENDARY', 73, 'интриги', types.FOR_ALL, types.LEGENDARY, FakeEffect(), []),

               ('ADD_PERSON_POWER_COMMON', 123, 'случай', types.FOR_PREMIUMS, types.COMMON, FakeEffect(), []),
               ('ADD_PERSON_POWER_UNCOMMON', 124, 'происки судьбы', types.FOR_PREMIUMS, types.UNCOMMON, FakeEffect(), []),
               ('ADD_PERSON_POWER_RARE', 125, 'неожиданное обстоятельство', types.FOR_PREMIUMS, types.RARE, FakeEffect(), []),
               ('ADD_PERSON_POWER_EPIC', 126, 'афера', types.FOR_PREMIUMS, types.EPIC, FakeEffect(), []),
               ('ADD_PERSON_POWER_LEGENDARY', 127, 'преступление века', types.FOR_PREMIUMS, types.LEGENDARY, FakeEffect(), []),

               ('ADD_PLACE_POWER_COMMON', 128, 'странные деньки', types.FOR_PREMIUMS, types.COMMON, FakeEffect(), []),
               ('ADD_PLACE_POWER_UNCOMMON', 129, 'происшествие', types.FOR_PREMIUMS, types.UNCOMMON, FakeEffect(), []),
               ('ADD_PLACE_POWER_RARE', 130, 'судьбоносный день', types.FOR_PREMIUMS, types.RARE, FakeEffect(), []),
               ('ADD_PLACE_POWER_EPIC', 131, 'экономический кризис', types.FOR_PREMIUMS, types.EPIC, FakeEffect(), []),
               ('ADD_PLACE_POWER_LEGENDARY', 132, 'политический кризис', types.FOR_PREMIUMS, types.LEGENDARY, FakeEffect(), []),

               ('LEVEL_UP', 1, 'озарение', types.FOR_ALL, types.LEGENDARY, FakeEffect(), []))


def constructor(type, **kwargs):

    def real_constructor(removed_card):
        return type.effect.create_card(type,
                                       available_for_auction=removed_card.available_for_auction,
                                       **kwargs)

    return real_constructor


CONSTRUCTORS_MAP = {
    '1': constructor(type=types.CARD.ADD_EXPERIENCE_LEGENDARY),

    '70': constructor(type=types.CARD.ADD_POWER_UNCOMMON),
    '71': constructor(type=types.CARD.QUEST_FOR_PLACE),
    '72': constructor(type=types.CARD.QUEST_FOR_PERSON),
    '73': constructor(type=types.CARD.ADD_POWER_LEGENDARY),

    '123': constructor(type=types.CARD.QUEST_FOR_EMISSARY),
    '124': constructor(type=types.CARD.ADD_POWER_UNCOMMON),
    '125': constructor(type=types.CARD.QUEST_FOR_PLACE),
    '126': constructor(type=types.CARD.QUEST_FOR_PERSON),
    '127': constructor(type=types.CARD.ADD_POWER_LEGENDARY),

    '128': constructor(type=types.CARD.QUEST_FOR_EMISSARY),
    '129': constructor(type=types.CARD.ADD_POWER_UNCOMMON),
    '130': constructor(type=types.CARD.QUEST_FOR_PLACE),
    '131': constructor(type=types.CARD.QUEST_FOR_PERSON),
    '132': constructor(type=types.CARD.ADD_POWER_LEGENDARY)
    }


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

            self.logger.info('replaced: ', len(added_cards))

            total_replaced += len(added_cards)

        self.logger.info(f'total replaced: {total_replaced}')
