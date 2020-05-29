
import smart_imports

smart_imports.all()


def actual_bills_accepted_timestamps(account_id):
    time_border = datetime.datetime.now() - datetime.timedelta(days=conf.settings.BILL_ACTUAL_LIVE_TIME)
    bills_ends = models.Bill.objects.filter(state=relations.BILL_STATE.ACCEPTED,
                                            owner=account_id,
                                            voting_end_at__gt=time_border).values_list('voting_end_at', flat=True)
    return [utils_logic.to_timestamp(accepted_time) for accepted_time in bills_ends]


def update_actual_bills_for_all_accounts():
    for account_id in models.Bill.objects.filter(state=relations.BILL_STATE.ACCEPTED).order_by('owner_id').values_list('owner_id', flat=True).distinct():
        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)
        account.update_actual_bills()
        account.save()


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
