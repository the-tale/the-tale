# coding: utf-8

from django.dispatch import receiver

from the_tale.game.bills import signals as bills_signals
from the_tale.game.bills import relations as bill_relations

from the_tale.game.chronicle import records
from the_tale.game.chronicle.relations import ACTOR_ROLE


def _get_bill_place_renaming_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_place_description_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_place_modifier_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_place_race_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_person_remove_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'text': bill.chronicle_on_accepted }

def _get_bill_person_move_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place),
                        (ACTOR_ROLE.PLACE, bill.data.new_place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'text': bill.chronicle_on_accepted }

def _get_bill_person_chronicle_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'text': bill.chronicle_on_accepted }

def _get_bill_place_chronicle_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_building_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'text': bill.chronicle_on_accepted }

def _get_bill_building_rename_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'text': bill.chronicle_on_accepted }

def _get_bill_place_resource_exchange_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place_1),
                        (ACTOR_ROLE.PLACE, bill.data.place_2)],
             'text': bill.chronicle_on_accepted}

def _get_bill_place_resource_conversion_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'text': bill.chronicle_on_accepted }

def _get_bill_persons_add_social_connection_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place_1),
                        (ACTOR_ROLE.PLACE, bill.data.place_2),
                        (ACTOR_ROLE.PERSON, bill.data.person_1),
                        (ACTOR_ROLE.PERSON, bill.data.person_2)],
             'text': bill.chronicle_on_accepted }


def _get_bill_persons_remove_social_connection_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place_1),
                        (ACTOR_ROLE.PLACE, bill.data.place_2),
                        (ACTOR_ROLE.PERSON, bill.data.person_1),
                        (ACTOR_ROLE.PERSON, bill.data.person_2)],
             'text': bill.chronicle_on_accepted }

def _get_bill_decline_bill_arguments(bill):
    if bill.data.declined_bill.data.type.is_PLACE_RESOURCE_EXCHANGE:
        actors = [(ACTOR_ROLE.BILL, bill),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_1),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_2)]
    elif bill.data.declined_bill.data.type.is_PLACE_RESOURCE_CONVERSION:
        actors = [(ACTOR_ROLE.BILL, bill),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place)]

    actors_ids = [(role, actor.id) for role, actor in actors]

    declined_bill_actors = BILL_ARGUMENT_GETTERS[bill.data.declined_bill.data.type](bill.data.declined_bill)['actors']

    for role, actor in declined_bill_actors:
        if (role, actor.id) not in actors_ids:
            actors.append((role, actor))

    return { 'actors': actors,
             'text': bill.chronicle_on_accepted}


BILL_ARGUMENT_GETTERS = {
    bill_relations.BILL_TYPE.PLACE_RENAMING: _get_bill_place_renaming_arguments,
    bill_relations.BILL_TYPE.PLACE_DESCRIPTION: _get_bill_place_description_arguments,
    bill_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER: _get_bill_place_modifier_arguments,
    bill_relations.BILL_TYPE.PLACE_CHANGE_RACE: _get_bill_place_race_arguments,
    bill_relations.BILL_TYPE.PERSON_REMOVE: _get_bill_person_remove_arguments,
    bill_relations.BILL_TYPE.PERSON_MOVE: _get_bill_person_move_arguments,
    bill_relations.BILL_TYPE.BUILDING_CREATE: _get_bill_building_arguments,
    bill_relations.BILL_TYPE.BUILDING_DESTROY: _get_bill_building_arguments,
    bill_relations.BILL_TYPE.BUILDING_RENAMING: _get_bill_building_rename_arguments,
    bill_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE: _get_bill_place_resource_exchange_arguments,
    bill_relations.BILL_TYPE.BILL_DECLINE: _get_bill_decline_bill_arguments,
    bill_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION: _get_bill_place_resource_conversion_arguments,
    bill_relations.BILL_TYPE.PERSON_CHRONICLE: _get_bill_person_chronicle_arguments,
    bill_relations.BILL_TYPE.PLACE_CHRONICLE: _get_bill_place_chronicle_arguments,
    bill_relations.BILL_TYPE.PERSON_ADD_SOCIAL_CONNECTION: _get_bill_persons_add_social_connection_arguments,
    bill_relations.BILL_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION: _get_bill_persons_remove_social_connection_arguments   }


@receiver(bills_signals.bill_processed, dispatch_uid='chronicle_bill_processed')
def chronicle_bill_processed(sender, bill, **kwargs): # pylint: disable=R0912,W0613

    if not bill.state.is_ACCEPTED:
        return

    record_type = { bill_relations.BILL_TYPE.PLACE_RENAMING: records.PlaceChangeNameBillSuccessed,
                    bill_relations.BILL_TYPE.PLACE_DESCRIPTION: records.PlaceChangeDescriptionBillSuccessed,
                    bill_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER: records.PlaceChangeModifierBillSuccessed,
                    bill_relations.BILL_TYPE.PLACE_CHANGE_RACE: records.PlaceChangeRaceBillSuccessed,
                    bill_relations.BILL_TYPE.PERSON_MOVE: records.PersonMoveBillSuccessed,
                    bill_relations.BILL_TYPE.BUILDING_CREATE: records.BuildingCreateBillSuccessed,
                    bill_relations.BILL_TYPE.BUILDING_DESTROY: records.BuildingDestroyBillSuccessed,
                    bill_relations.BILL_TYPE.BUILDING_RENAMING: records.BuildingRenamingBillSuccessed,
                    bill_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE: records.PlaceResourceExchangeBillSuccessed,
                    bill_relations.BILL_TYPE.BILL_DECLINE: records.BillDeclineSuccessed,
                    bill_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION: records.PlaceResourceConversionBillSuccessed,
                    bill_relations.BILL_TYPE.PERSON_CHRONICLE: records.PersonChronicleBillSuccessed,
                    bill_relations.BILL_TYPE.PLACE_CHRONICLE: records.PlaceChronicleBillSuccessed,
                    bill_relations.BILL_TYPE.PERSON_ADD_SOCIAL_CONNECTION: records.PersonAddSocialConnection,
                    bill_relations.BILL_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION: records.PersonRemoveSocialConnection,
                  }[bill.data.type]

    record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
