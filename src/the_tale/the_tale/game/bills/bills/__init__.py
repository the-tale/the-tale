
import smart_imports

smart_imports.all()


BILLS = [place_renaming.PlaceRenaming,
         place_description.PlaceDescripton,
         place_change_modifier.PlaceModifier,
         person_remove.PersonRemove,
         building_create.BuildingCreate,
         building_destroy.BuildingDestroy,
         building_renaming.BuildingRenaming,
         place_resource_exchange.PlaceResourceExchange,
         place_resource_conversion.PlaceResourceConversion,
         bill_decline.BillDecline,
         person_chronicle.PersonChronicle,
         place_chronicle.PlaceChronicle,
         person_move.PersonMove,
         place_change_race.PlaceRace,
         person_add_social_connection.PersonAddSocialConnection,
         person_remove_social_connection.PersonRemoveSocialConnection,
         road_create.RoadCreate,
         road_destroy.RoadDestroy,
         road_change.RoadChange,
         emissary_chronicle.EmissaryChronicle,
         place_change_tax_size_border.PlaceTaxSizeBorder]


def deserialize_bill(data):
    return BILLS_BY_STR[data['type']].deserialize(data)


BILLS_BY_ID = dict((bill.type.value, bill) for bill in BILLS)
BILLS_BY_STR = dict((bill.type.name.lower(), bill) for bill in BILLS)

# TODO: migrate old bills to new name and remove that line
BILLS_BY_STR['place_modifier'] = BILLS_BY_STR['place_change_modifier']
