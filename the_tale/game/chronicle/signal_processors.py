# coding: utf-8

from django.dispatch import receiver

from textgen.words import Fake as FakeWord

from the_tale.game.bills import signals as bills_signals
from the_tale.game.bills.models import BILL_TYPE

from the_tale.game.map.places import signals as places_signals

from the_tale.game.chronicle import records
from the_tale.game.chronicle.relations import ACTOR_ROLE


def _get_bill_place_renaming_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {'bill': FakeWord(bill.caption),
                               'old_name': bill.data.old_name_forms,
                               'new_name': bill.data.name_forms} }

def _get_bill_place_description_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {'place': bill.data.place,
                               'bill': FakeWord(bill.caption)} }

def _get_bill_place_modifier_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {'place': bill.data.place,
                               'bill': FakeWord(bill.caption),
                               'old_modifier': bill.data.place.modifier.NAME.lower() if bill.data.place.modifier is not None else None,
                               'new_modifier': bill.data.modifier_name.lower()} }

def _get_bill_person_remove_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {'place': bill.data.person.place,
                               'person': bill.data.person,
                               'bill': FakeWord(bill.caption)} }

def _get_bill_building_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {'place': bill.data.person.place,
                               'person': bill.data.person,
                               'bill': FakeWord(bill.caption)} }

def _get_bill_building_rename_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {'place': bill.data.person.place,
                               'person': bill.data.person,
                               'old_name': bill.data.old_building_name_forms,
                               'new_name': bill.data.new_building_name_forms,
                               'bill': FakeWord(bill.caption)} }

def _get_bill_place_resource_exchange_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place_1),
                        (ACTOR_ROLE.PLACE, bill.data.place_2)],
             'substitutions': {'place_1': bill.data.place_1,
                               'place_2': bill.data.place_2,
                               'resource_1': FakeWord(bill.data.resource_1.text),
                               'resource_2': FakeWord(bill.data.resource_2.text),
                               'bill': FakeWord(bill.caption)} }

def _get_bill_place_resource_conversion_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {'place': bill.data.place,
                               'conversion': FakeWord(bill.data.conversion.text),
                               'bill': FakeWord(bill.caption)} }

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
             'substitutions': {'declined_bill': FakeWord(bill.data.declined_bill.caption),
                               'bill': FakeWord(bill.caption)} }


BILL_ARGUMENT_GETTERS = {
    BILL_TYPE.PLACE_RENAMING: _get_bill_place_renaming_arguments,
    BILL_TYPE.PLACE_DESCRIPTION: _get_bill_place_description_arguments,
    BILL_TYPE.PLACE_MODIFIER: _get_bill_place_modifier_arguments,
    BILL_TYPE.PERSON_REMOVE: _get_bill_person_remove_arguments,
    BILL_TYPE.BUILDING_CREATE: _get_bill_building_arguments,
    BILL_TYPE.BUILDING_DESTROY: _get_bill_building_arguments,
    BILL_TYPE.BUILDING_RENAMING: _get_bill_building_rename_arguments,
    BILL_TYPE.PLACE_RESOURCE_EXCHANGE: _get_bill_place_resource_exchange_arguments,
    BILL_TYPE.BILL_DECLINE: _get_bill_decline_bill_arguments,
    BILL_TYPE.PLACE_RESOURCE_CONVERSION: _get_bill_place_resource_conversion_arguments,}



@receiver(bills_signals.bill_moderated, dispatch_uid='chronicle_bill_moderated')
def chronicle_bill_moderated(sender, bill, **kwargs): # pylint: disable=W0613
    if not bill.approved_by_moderator: return

    if bill.data.type == BILL_TYPE.PLACE_RENAMING:
        records.PlaceChangeNameBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_DESCRIPTION:
        records.PlaceChangeDescriptionBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_MODIFIER:
        records.PlaceChangeModifierBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PERSON_REMOVE:
        records.PersonRemoveBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.BUILDING_CREATE:
        records.BuildingCreateBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.BUILDING_DESTROY:
        records.BuildingDestroyBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.BUILDING_RENAMING:
        records.BuildingRenamingBillStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_RESOURCE_EXCHANGE:
        records.PlaceResourceExchangeStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.BILL_DECLINE:
        records.BillDeclineStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_RESOURCE_CONVERSION:
        records.PlaceResourceConversionStarted(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

@receiver(bills_signals.bill_processed, dispatch_uid='chronicle_bill_processed')
def chronicle_bill_processed(sender, bill, **kwargs): # pylint: disable=R0912,W0613

    if bill.data.type == BILL_TYPE.PLACE_RENAMING:
        record_type = records.PlaceChangeNameBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PlaceChangeNameBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_DESCRIPTION:
        record_type = records.PlaceChangeDescriptionBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PlaceChangeDescriptionBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_MODIFIER:
        record_type = records.PlaceChangeModifierBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PlaceChangeModifierBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.PERSON_REMOVE:
        record_type = records.PersonRemoveBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PersonRemoveBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.BUILDING_CREATE:
        record_type = records.BuildingCreateBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.BuildingCreateBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.BUILDING_DESTROY:
        record_type = records.BuildingDestroyBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.BuildingDestroyBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.BUILDING_RENAMING:
        record_type = records.BuildingRenamingBillFailed
        if bill.state.is_ACCEPTED:
            record_type = records.BuildingRenamingBillSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_RESOURCE_EXCHANGE:
        record_type = records.PlaceResourceExchangeFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PlaceResourceExchangeSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.BILL_DECLINE:
        record_type = records.BillDeclineFailed
        if bill.state.is_ACCEPTED:
            record_type = records.BillDeclineSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_RESOURCE_CONVERSION:
        record_type = records.PlaceResourceConversionFailed
        if bill.state.is_ACCEPTED:
            record_type = records.PlaceResourceConversionSuccessed
        record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()


@receiver(bills_signals.bill_ended, dispatch_uid='chronicle_bill_ended')
def chronicle_bill_ended(sender, bill, **kwargs): # pylint: disable=R0912,W0613
    if bill.data.type == BILL_TYPE.PLACE_RESOURCE_EXCHANGE:
        records.PlaceResourceExchangeEnded(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_RESOURCE_CONVERSION:
        records.PlaceResourceConversionEnded(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()



@receiver(places_signals.place_modifier_reseted, dispatch_uid='chronicle_place_modifier_reseted')
def chronicle_place_modifier_reseted(sender, place, old_modifier, **kwargs): # pylint: disable=W0613
    records.PlaceLosedModifier(actors=[(ACTOR_ROLE.PLACE, place)],
                               substitutions={'place': place,
                                              'old_modifier': old_modifier.NAME.lower()}).create_record()

@receiver(places_signals.place_person_left, dispatch_uid='chronicle_place_person_left')
def chronicle_place_person_left(sender, place, person, **kwargs): # pylint: disable=W0613
    records.PersonLeftPlace(actors=[(ACTOR_ROLE.PLACE, place),
                                    (ACTOR_ROLE.PERSON, person)],
                            substitutions={'place': place,
                                           'person': person}).create_record()

@receiver(places_signals.place_person_arrived, dispatch_uid='chronicle_place_person_arrived')
def chronicle_place_person_arrived(sender, place, person, **kwargs): # pylint: disable=W0613
    records.PersonArrivedToPlace(actors=[(ACTOR_ROLE.PLACE, place),
                                         (ACTOR_ROLE.PERSON, person)],
                                 substitutions={'place':place,
                                                'person': person}).create_record()

@receiver(places_signals.place_race_changed, dispatch_uid='chronicle_place_race_changed')
def chronicle_place_race_changed(sender, place, old_race, new_race, **kwargs): # pylint: disable=W0613
    records.PlaceChangeRace(actors=[(ACTOR_ROLE.PLACE, place)],
                            substitutions={'place': place,
                                           'old_race': old_race.text,
                                           'new_race': new_race.text}).create_record()


@receiver(places_signals.building_destroyed_by_amortization, dispatch_uid='chronicle_building_destroyed_by_amortization')
def chronicle_building_destroyed_by_amortization(sender, place, person, **kwargs): # pylint: disable=W0613
    records.BuildingDestroyedByAmortization(actors=[(ACTOR_ROLE.PLACE, place),
                                                    (ACTOR_ROLE.PERSON, person)],
                                            substitutions={'place': place,
                                                           'person': person}).create_record()
