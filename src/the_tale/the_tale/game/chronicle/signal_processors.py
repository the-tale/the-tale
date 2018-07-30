
import smart_imports

smart_imports.all()


def _get_bill_place_renaming_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_description_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_modifier_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_race_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_person_remove_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.person.place),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person)],
            'text': bill.chronicle_on_accepted}


def _get_bill_person_move_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.new_place),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person)],
            'text': bill.chronicle_on_accepted}


def _get_bill_person_chronicle_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.person.place),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_chronicle_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_building_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.person.place),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person)],
            'text': bill.chronicle_on_accepted}


def _get_bill_building_rename_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.person.place),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_resource_exchange_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_1),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_2)],
            'text': bill.chronicle_on_accepted}


def _get_bill_place_resource_conversion_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place)],
            'text': bill.chronicle_on_accepted}


def _get_bill_persons_add_social_connection_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_1),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_2),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person_1),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person_2)],
            'text': bill.chronicle_on_accepted}


def _get_bill_persons_remove_social_connection_arguments(bill):
    return {'actors': [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_1),
                       (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.place_2),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person_1),
                       (chronicle_relations.ACTOR_ROLE.PERSON, bill.data.person_2)],
            'text': bill.chronicle_on_accepted}


def _get_bill_decline_bill_arguments(bill):
    if bill.data.declined_bill.data.type.is_PLACE_RESOURCE_EXCHANGE:
        actors = [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                  (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_1),
                  (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_2)]
    elif bill.data.declined_bill.data.type.is_PLACE_RESOURCE_CONVERSION:
        actors = [(chronicle_relations.ACTOR_ROLE.BILL, bill),
                  (chronicle_relations.ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place)]

    actors_ids = [(role, actor.id) for role, actor in actors]

    declined_bill_actors = BILL_ARGUMENT_GETTERS[bill.data.declined_bill.data.type](bill.data.declined_bill)['actors']

    for role, actor in declined_bill_actors:
        if (role, actor.id) not in actors_ids:
            actors.append((role, actor))

    return {'actors': actors,
            'text': bill.chronicle_on_accepted}


BILL_ARGUMENT_GETTERS = {
    bills_relations.BILL_TYPE.PLACE_RENAMING: _get_bill_place_renaming_arguments,
    bills_relations.BILL_TYPE.PLACE_DESCRIPTION: _get_bill_place_description_arguments,
    bills_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER: _get_bill_place_modifier_arguments,
    bills_relations.BILL_TYPE.PLACE_CHANGE_RACE: _get_bill_place_race_arguments,
    bills_relations.BILL_TYPE.PERSON_REMOVE: _get_bill_person_remove_arguments,
    bills_relations.BILL_TYPE.PERSON_MOVE: _get_bill_person_move_arguments,
    bills_relations.BILL_TYPE.BUILDING_CREATE: _get_bill_building_arguments,
    bills_relations.BILL_TYPE.BUILDING_DESTROY: _get_bill_building_arguments,
    bills_relations.BILL_TYPE.BUILDING_RENAMING: _get_bill_building_rename_arguments,
    bills_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE: _get_bill_place_resource_exchange_arguments,
    bills_relations.BILL_TYPE.BILL_DECLINE: _get_bill_decline_bill_arguments,
    bills_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION: _get_bill_place_resource_conversion_arguments,
    bills_relations.BILL_TYPE.PERSON_CHRONICLE: _get_bill_person_chronicle_arguments,
    bills_relations.BILL_TYPE.PLACE_CHRONICLE: _get_bill_place_chronicle_arguments,
    bills_relations.BILL_TYPE.PERSON_ADD_SOCIAL_CONNECTION: _get_bill_persons_add_social_connection_arguments,
    bills_relations.BILL_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION: _get_bill_persons_remove_social_connection_arguments}


@django_dispatch.receiver(bills_signals.bill_processed, dispatch_uid='chronicle_bill_processed')
def chronicle_bill_processed(sender, bill, **kwargs):  # pylint: disable=R0912,W0613

    if not bill.state.is_ACCEPTED:
        return

    record_type = {bills_relations.BILL_TYPE.PLACE_RENAMING: records.PlaceChangeNameBillSuccessed,
                   bills_relations.BILL_TYPE.PLACE_DESCRIPTION: records.PlaceChangeDescriptionBillSuccessed,
                   bills_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER: records.PlaceChangeModifierBillSuccessed,
                   bills_relations.BILL_TYPE.PLACE_CHANGE_RACE: records.PlaceChangeRaceBillSuccessed,
                   bills_relations.BILL_TYPE.PERSON_MOVE: records.PersonMoveBillSuccessed,
                   bills_relations.BILL_TYPE.BUILDING_CREATE: records.BuildingCreateBillSuccessed,
                   bills_relations.BILL_TYPE.BUILDING_DESTROY: records.BuildingDestroyBillSuccessed,
                   bills_relations.BILL_TYPE.BUILDING_RENAMING: records.BuildingRenamingBillSuccessed,
                   bills_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE: records.PlaceResourceExchangeBillSuccessed,
                   bills_relations.BILL_TYPE.BILL_DECLINE: records.BillDeclineSuccessed,
                   bills_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION: records.PlaceResourceConversionBillSuccessed,
                   bills_relations.BILL_TYPE.PERSON_CHRONICLE: records.PersonChronicleBillSuccessed,
                   bills_relations.BILL_TYPE.PLACE_CHRONICLE: records.PlaceChronicleBillSuccessed,
                   bills_relations.BILL_TYPE.PERSON_ADD_SOCIAL_CONNECTION: records.PersonAddSocialConnection,
                   bills_relations.BILL_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION: records.PersonRemoveSocialConnection,
                   }[bill.data.type]

    record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
