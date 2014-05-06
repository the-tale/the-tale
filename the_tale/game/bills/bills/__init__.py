# coding: utf-8

from the_tale.game.bills.bills.place_renaming import PlaceRenaming
from the_tale.game.bills.bills.place_description import PlaceDescripton
from the_tale.game.bills.bills.place_change_modifier import PlaceModifier
from the_tale.game.bills.bills.person_remove import PersonRemove
from the_tale.game.bills.bills.building_create import BuildingCreate
from the_tale.game.bills.bills.building_destroy import BuildingDestroy
from the_tale.game.bills.bills.building_renaming import BuildingRenaming
from the_tale.game.bills.bills.place_resource_exchange import PlaceResourceExchange
from the_tale.game.bills.bills.place_resource_conversion import PlaceResourceConversion
from the_tale.game.bills.bills.bill_decline import BillDecline


BILLS = [PlaceRenaming,
         PlaceDescripton,
         PlaceModifier,
         PersonRemove,
         BuildingCreate,
         BuildingDestroy,
         BuildingRenaming,
         PlaceResourceExchange,
         PlaceResourceConversion,
         BillDecline]

def deserialize_bill(data):
    return BILLS_BY_STR[data['type']].deserialize(data)


BILLS_BY_ID = dict( (bill.type.value, bill) for bill in BILLS)
BILLS_BY_STR = dict( (bill.type.name.lower(), bill) for bill in BILLS)
