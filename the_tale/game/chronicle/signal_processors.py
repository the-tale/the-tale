# coding: utf-8

from django.dispatch import receiver

from textgen.words import Fake as FakeWord

from game.bills import signals as bills_signals
from game.bills import BILL_TYPE

from game.map.places import signals as places_signals

from game.chronicle import records
from game.chronicle.relations import ACTOR_ROLE


def _get_bill_place_renaming_arguments(bill):
    return { 'actors': {ACTOR_ROLE.BILL: bill,
                        ACTOR_ROLE.PLACE: bill.data.place},
             'substitutions': {'bill': FakeWord(bill.caption),
                               'old_name': bill.data.old_name_forms,
                               'new_name': bill.data.name_forms} }

def _get_bill_place_description_arguments(bill):
    return { 'actors': {ACTOR_ROLE.BILL: bill,
                        ACTOR_ROLE.PLACE: bill.data.place},
             'substitutions': {'place': bill.data.place,
                               'bill': FakeWord(bill.caption)} }

def _get_bill_place_modifier_arguments(bill):
    return { 'actors': {ACTOR_ROLE.BILL: bill,
                        ACTOR_ROLE.PLACE: bill.data.place},
             'substitutions': {'place': bill.data.place,
                               'bill': FakeWord(bill.caption),
                               'old_modifier': bill.data.place.modifier.NAME.lower() if bill.data.place.modifier is not None else None,
                               'new_modifier': bill.data.modifier_name.lower()} }

def _get_bill_person_remove_arguments(bill):
    return { 'actors': {ACTOR_ROLE.BILL: bill,
                        ACTOR_ROLE.PLACE: bill.data.person.place,
                        ACTOR_ROLE.PERSON: bill.data.person},
             'substitutions': {'place': bill.data.person.place,
                               'person': bill.data.person,
                               'bill': FakeWord(bill.caption)} }


@receiver(bills_signals.bill_moderated, dispatch_uid='chronicle_bill_moderated')
def chronicle_bill_moderated(sender, bill, **kwargs):
    if not bill.approved_by_moderator: return

    if bill.data.type == BILL_TYPE.PLACE_RENAMING:
        records.PlaceChangeNameBillStarted(**_get_bill_place_renaming_arguments(bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_DESCRIPTION:
        records.PlaceChangeDescriptionBillStarted(**_get_bill_place_description_arguments(bill)).create_record()
    elif bill.data.type == BILL_TYPE.PLACE_MODIFIER:
        records.PlaceChangeModifierBillStarted(**_get_bill_place_modifier_arguments(bill)).create_record()
    elif bill.data.type == BILL_TYPE.PERSON_REMOVE:
        records.PersonRemoveBillStarted(**_get_bill_person_remove_arguments(bill)).create_record()

@receiver(bills_signals.bill_processed, dispatch_uid='chronicle_bill_processed')
def chronicle_bill_processed(sender, bill, **kwargs):

    if bill.data.type == BILL_TYPE.PLACE_RENAMING:
        record_type = records.PlaceChangeNameBillFailed
        if bill.state._is_ACCEPTED:
            record_type = records.PlaceChangeNameBillSuccessed
        record_type(**_get_bill_place_renaming_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_DESCRIPTION:
        record_type = records.PlaceChangeDescriptionBillFailed
        if bill.state._is_ACCEPTED:
            record_type = records.PlaceChangeDescriptionBillSuccessed
        record_type(**_get_bill_place_description_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_MODIFIER:
        record_type = records.PlaceChangeModifierBillFailed
        if bill.state._is_ACCEPTED:
            record_type = records.PlaceChangeModifierBillSuccessed
        record_type(**_get_bill_place_modifier_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PERSON_REMOVE:
        record_type = records.PersonRemoveBillFailed
        if bill.state._is_ACCEPTED:
            record_type = records.PersonRemoveBillSuccessed
        record_type(**_get_bill_person_remove_arguments(bill)).create_record()

@receiver(places_signals.place_modifier_reseted, dispatch_uid='chronicle_place_modifier_reseted')
def chronicle_place_modifier_reseted(sender, place, old_modifier, **kwargs):
    records.PlaceLosedModifier(actors={ACTOR_ROLE.PLACE: place},
                               substitutions={'place': place,
                                              'old_modifier': old_modifier.NAME.lower()}).create_record()

@receiver(places_signals.place_person_left, dispatch_uid='chronicle_place_person_left')
def chronicle_place_person_left(sender, place, person, **kwargs):
    records.PersonLeftPlace(actors={ACTOR_ROLE.PLACE: place,
                                    ACTOR_ROLE.PERSON: person},
                            substitutions={'place': place,
                                           'person': person}).create_record()

@receiver(places_signals.place_person_arrived, dispatch_uid='chronicle_place_person_arrived')
def chronicle_place_person_arrived(sender, place, person, **kwargs):
    records.PersonArrivedToPlace(actors={ACTOR_ROLE.PLACE: place,
                                         ACTOR_ROLE.PERSON: person},
                                 substitutions={'place':place,
                                                'person': person}).create_record()

@receiver(places_signals.place_race_changed, dispatch_uid='chronicle_place_race_changed')
def chronicle_place_race_changed(sender, place, old_race, new_race, **kwargs):
    records.PlaceChangeRace(actors={ACTOR_ROLE.PLACE: place},
                            substitutions={'place': place,
                                           'old_race': old_race.verbose,
                                           'new_race': new_race.verbose}).create_record()
