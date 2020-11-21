
import smart_imports

smart_imports.all()


def receive_cards_url():
    return utils_urls.url('game:cards:api-receive-cards', api_version=conf.settings.RECEIVE_API_VERSION, api_client=django_settings.API_CLIENT)


def combine_cards_url(api_version=None):
    if api_version is None:
        api_version = conf.settings.COMBINE_API_VERSION

    return utils_urls.url('game:cards:api-combine', api_version=api_version, api_client=django_settings.API_CLIENT)


def move_to_storage_url():
    return utils_urls.url('game:cards:api-move-to-storage', api_version=conf.settings.MOVE_TO_STORAGE_API_VERSION, api_client=django_settings.API_CLIENT)


def move_to_hand_url():
    return utils_urls.url('game:cards:api-move-to-hand', api_version=conf.settings.MOVE_TO_HAND_API_VERSION, api_client=django_settings.API_CLIENT)


def use_card_url(card_uid):
    return utils_urls.url('game:cards:api-use', card=card_uid, api_version=conf.settings.USE_API_VERSION, api_client=django_settings.API_CLIENT)


def get_cards_url():
    return utils_urls.url('game:cards:api-get-cards', api_version=conf.settings.GET_CARDS_API_VERSION, api_client=django_settings.API_CLIENT)


def transform_cards_url():
    return utils_urls.url('game:cards:api-combine', api_version=conf.settings.COMBINE_API_VERSION, api_client=django_settings.API_CLIENT)


def change_receive_mode_url(mode):
    return utils_urls.url('game:cards:api-change-receive-mode',
                          api_version=conf.settings.CHANGE_RECEIVE_MODE_API_VERSION,
                          api_client=django_settings.API_CLIENT,
                          mode=mode.value)


def create_card(allow_premium_cards, rarity=None, exclude=(), available_for_auction=False):
    cards_types = list(types.CARD.records)

    if not allow_premium_cards:
        cards_types = [card for card in cards_types if not card.availability.is_FOR_PREMIUMS]

    if rarity:
        cards_types = [card for card in cards_types if card.rarity == rarity]

    cards_choices = [card.effect.create_card(available_for_auction=available_for_auction, type=card)
                     for card in cards_types
                     if card.effect.available(card)]

    if exclude:
        cards_choices = [card for card in cards_choices if not any(card.is_same_effect(excluded_card) for excluded_card in exclude)]

    prioritites = [(card, card.type.rarity.priority) for card in cards_choices]

    return utils_logic.random_value_by_priority(prioritites)


def get_combined_cards(allow_premium_cards, combined_cards):
    if not combined_cards:
        return None, relations.COMBINED_CARD_RESULT.NO_CARDS

    if len({card.type.rarity for card in combined_cards}) != 1:
        return None, relations.COMBINED_CARD_RESULT.EQUAL_RARITY_REQUIRED

    if len(combined_cards) != len({card.uid for card in combined_cards}):
        return None, relations.COMBINED_CARD_RESULT.DUPLICATE_IDS

    available_for_auction = all(card.available_for_auction for card in combined_cards)

    if len(combined_cards) == 1:
        return get_combined_cards_1(combined_cards, allow_premium_cards, available_for_auction)

    if len(combined_cards) == 2:
        return get_combined_cards_2(combined_cards, allow_premium_cards, available_for_auction)

    if len(combined_cards) == 3:
        return get_combined_cards_3(combined_cards, allow_premium_cards, available_for_auction)

    return get_combined_cards_more_then_3(combined_cards, allow_premium_cards, available_for_auction)


def get_combined_cards_1(combined_cards, allow_premium_cards, available_for_auction):
    if combined_cards[0].type.rarity.is_COMMON:
        return None, relations.COMBINED_CARD_RESULT.COMBINE_1_COMMON

    for reactor in combined_cards[0].type.combiners:
        cards = reactor.combine(combined_cards)
        if cards:
            return cards, relations.COMBINED_CARD_RESULT.SUCCESS

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=relations.RARITY(combined_cards[0].type.rarity.value - 1),
                       available_for_auction=available_for_auction)

    return [card], relations.COMBINED_CARD_RESULT.SUCCESS


def get_combined_cards_2(combined_cards, allow_premium_cards, available_for_auction):

    for reactor in combined_cards[0].type.combiners:
        cards = reactor.combine(combined_cards)
        if cards:
            return cards, relations.COMBINED_CARD_RESULT.SUCCESS

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=combined_cards[0].type.rarity,
                       exclude=combined_cards,
                       available_for_auction=available_for_auction)

    return [card], relations.COMBINED_CARD_RESULT.SUCCESS


def get_combined_cards_3(combined_cards, allow_premium_cards, available_for_auction):

    for reactor in combined_cards[0].type.combiners:
        cards = reactor.combine(combined_cards)
        if cards:
            return cards, relations.COMBINED_CARD_RESULT.SUCCESS

    if combined_cards[0].type.rarity.is_LEGENDARY:
        return None, relations.COMBINED_CARD_RESULT.COMBINE_3_LEGENDARY

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=relations.RARITY(combined_cards[0].type.rarity.value + 1),
                       available_for_auction=available_for_auction)

    return [card], relations.COMBINED_CARD_RESULT.SUCCESS


def get_combined_cards_more_then_3(combined_cards, allow_premium_cards, available_for_auction):

    for reactor in combined_cards[0].type.combiners:
        cards = reactor.combine(combined_cards)
        if cards:
            return cards, relations.COMBINED_CARD_RESULT.SUCCESS

    return None, relations.COMBINED_CARD_RESULT.TOO_MANY_CARDS


def get_cards_info_by_full_types():
    cards_info = {}

    for card in types.CARD.records:
        names = card.effect.full_type_names(card)

        for full_type, name in names.items():
            cards_info[full_type] = {'name': name, 'card': card}

    return cards_info


def give_new_cards(account_id, operation_type, allow_premium_cards, available_for_auction, rarity=None, number=1):

    cards = []

    for i in range(number):
        cards.append(create_card(rarity=rarity,
                                 allow_premium_cards=allow_premium_cards,
                                 available_for_auction=available_for_auction))

    change_cards(owner_id=account_id,
                 operation_type=operation_type,
                 storage=relations.STORAGE.NEW,
                 to_add=cards)


def change_cards(owner_id, operation_type, to_add=(), to_remove=(), storage=relations.STORAGE.FAST):
    operations = []

    for card in to_remove:
        operations.append(tt_services.storage.Destroy(owner_id=owner_id, card=card))

    for card in to_add:
        operations.append(tt_services.storage.Create(owner_id=owner_id, card=card, storage=storage))

    tt_services.storage.cmd_apply(operations, operation_type)


def change_owner(old_owner_id, new_owner_id, operation_type, new_storage, cards_ids):
    operations = []

    for card_id in cards_ids:
        operations.append(tt_services.storage.ChangeOwner(card_id=card_id,
                                                          old_owner_id=old_owner_id,
                                                          new_owner_id=new_owner_id,
                                                          new_storage=new_storage))

    tt_services.storage.cmd_apply(operations, operation_type)


def change_storage(owner_id, operation_type, cards, old_storage, new_storage):
    operations = []

    for card in cards:
        operations.append(tt_services.storage.ChangeStorage(owner_id=owner_id,
                                                            card=card,
                                                            old_storage=old_storage,
                                                            new_storage=new_storage))

    tt_services.storage.cmd_apply(operations, operation_type)


def has_cards(owner_id, cards_ids):
    return tt_services.storage.cmd_has_items(owner_id, [id.hex for id in cards_ids])


def get_card_probability(type):
    return type.rarity.priority / sum(card.rarity.priority for card in types.CARD.records)


def is_companion_card_rarity_mismatch(card):
    if card.type not in (types.CARD.GET_COMPANION_COMMON,
                         types.CARD.GET_COMPANION_UNCOMMON,
                         types.CARD.GET_COMPANION_RARE,
                         types.CARD.GET_COMPANION_EPIC,
                         types.CARD.GET_COMPANION_LEGENDARY):
        return False

    companion_id = card.data['companion_id']

    return card.type.rarity != companions_storage.companions[companion_id].rarity.card_rarity
