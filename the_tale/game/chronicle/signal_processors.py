# coding: utf-8

from django.dispatch import receiver

from game.bills import signals as bills_signals
from game.bills import BILL_TYPE

from game.chronicle import records

# BILL_TYPE = create_enum('BILL_TYPE', (('PLACE_RENAMING', 0, u'переименование места'),
#                                       ('PERSON_REMOVE', 1, u'удаление персонажа'),
#                                       ('PLACE_DESCRIPTION', 2, u'изменить описание места'),
#                                       ('PLACE_MODIFIER', 3, u'изменить тип места')))


def _get_bill_place_renaming_arguments(bill):
    return {'place': bill.data.place,
            'bill': bill,
            'old_name': bill.data.old_name_forms,
            'new_name': bill.data.name_forms}

def _get_bill_place_description_arguments(bill):
    return {'place': bill.data.place,
            'bill': bill}

def _get_bill_place_modifier_arguments(bill):
    return {'place': bill.data.place,
            'bill': bill,
            'old_modifier': bill.data.place.modifier.NAME.lower() if bill.data.place.modifier is not None else None,
            'new_modifier': bill.data.modifier_name}

def _get_bill_person_remove_arguments(bill):
    return {'place': bill.data.person.place,
            'person': bill.data.person,
            'bill': bill}


@receiver(bills_signals.bill_moderated, dispatch_uid="chronicle_bill_moderated")
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

@receiver(bills_signals.bill_processed, dispatch_uid="chronicle_bill_processed")
def chronicle_bill_processed(sender, bill, **kwargs):

    if bill.data.type == BILL_TYPE.PLACE_RENAMING:
        record_type = records.PlaceChangeNameBillFailed
        if bill.state.is_accepted:
            record_type = records.PlaceChangeNameBillSuccessed
        record_type(**_get_bill_place_renaming_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_DESCRIPTION:
        record_type = records.PlaceChangeDescriptionBillFailed
        if bill.state.is_accepted:
            record_type = records.PlaceChangeDescriptionBillSuccessed
        record_type(**_get_bill_place_description_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PLACE_MODIFIER:
        record_type = records.PlaceChangeModifierBillFailed
        if bill.state.is_accepted:
            record_type = records.PlaceChangeModifierBillSuccessed
        record_type(**_get_bill_place_modifier_arguments(bill)).create_record()

    elif bill.data.type == BILL_TYPE.PERSON_REMOVE:
        record_type = records.PersonRemoveBillFailed
        if bill.state.is_accepted:
            record_type = records.PersonRemoveBillSuccessed
        record_type(**_get_bill_person_remove_arguments(bill)).create_record()
