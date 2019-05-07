
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'return to players items, which added to shop storage, but not registered on market'

    def handle(self, *args, **options):

        items = cards_tt_services.storage.cmd_get_items(owner_id=accounts_logic.get_system_user_id())

        print('items found: ', len(items))

        for i, (item_id, item) in enumerate(items.items()):
            # print('[{}/{}] process item {}'.format(i, len(items), item_id))

            if shop_tt_services.market.cmd_does_lot_exist_for_item(item_type=item.item_full_type,
                                                                   item_id=item_id.hex):
                continue

            print('[{}/{}] lost item found: {}'.format(i, len(items), item_id))

            logs = cards_tt_services.storage.cmd_get_item_logs(item_id=item_id.hex)

            last_record = logs[-1]

            if last_record.data['operation_type'] != '#create_sell_lots':
                print('unknown last operation_type "{}", skip'.format(last_record.data['operation_type']))
                continue

            cards_logic.change_owner(old_owner_id=accounts_logic.get_system_user_id(),
                                     new_owner_id=last_record.data['old_owner_id'],
                                     operation_type='#resturn_lost_item',
                                     new_storage=cards_relations.STORAGE.FAST,
                                     cards_ids=[item_id])

            print('item returned to player {}'.format(last_record.data['old_owner_id']))
