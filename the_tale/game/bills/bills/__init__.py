# coding: utf-8

from game.bills.bills.place_renaming import PlaceRenaming
from game.bills.bills.place_description import PlaceDescripton
from game.bills.bills.place_change_modifier import PlaceModifier
from game.bills.bills.person_remove import PersonRemove
from game.bills.bills.building_create import BuildingCreate


BILLS = [PlaceRenaming, PlaceDescripton, PlaceModifier, PersonRemove, BuildingCreate]

def deserialize_bill(data):
    return BILLS_BY_STR[data['type']].deserialize(data)


BILLS_BY_ID = dict( (bill.type.value, bill) for bill in BILLS)
BILLS_BY_STR = dict( (bill.type.name.lower(), bill) for bill in BILLS)
