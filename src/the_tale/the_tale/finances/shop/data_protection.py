
import smart_imports

smart_imports.all()


def remove_data(account_id):

    lots = tt_services.market.cmd_list_sell_lots(owner_id=account_id)

    for lot in sorted(lots, key=lambda lot: lot.price):
        logic.cancel_sell_lot(item_type=lot.full_type,
                              price=lot.price,
                              account_id=account_id,
                              operation_type='#cancel_sell_lots_on_account_deletion')
