
import smart_imports

smart_imports.all()


def validate_bills():
    for active_bill_id in prototypes.BillPrototype.get_active_bills_ids():
        bill = prototypes.BillPrototype.get_by_id(active_bill_id)
        if not bill.has_meaning():
            bill.stop()


def apply_bills(logger):
    logger.info('apply bills')

    validate_bills()

    applied = False

    for applied_bill_id in prototypes.BillPrototype.get_applicable_bills_ids():
        bill = prototypes.BillPrototype.get_by_id(applied_bill_id)

        if bill.is_delayed:
            continue

        if bill.state.is_VOTING:
            applied = bill.apply() or applied

        validate_bills()

    logger.info('apply bills completed')

    return applied
