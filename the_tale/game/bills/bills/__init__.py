# coding: utf-8

from game.bills.bills.place_renaming import PlaceRenaming

BILLS = [PlaceRenaming]

def deserialize_bill(data):
    return BILLS_BY_STR[data['type']].deserialize(data)


BILLS_BY_ID = dict( (bill.type, bill) for bill in BILLS)
BILLS_BY_STR = dict( (bill.type_str, bill) for bill in BILLS)
