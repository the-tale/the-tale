# coding: utf-8
import time
import datetime

from the_tale import amqp_environment

from the_tale.accounts import prototypes as accounts_prototypes

from the_tale.game.bills import models
from the_tale.game.bills import relations
from the_tale.game.bills import conf


def actual_bills_accepted_timestamps(account_id):
    time_border = datetime.datetime.now() - datetime.timedelta(days=conf.bills_settings.BILL_ACTUAL_LIVE_TIME)
    bills_ends =  models.Bill.objects.filter(state=relations.BILL_STATE.ACCEPTED,
                                             owner=account_id,
                                             voting_end_at__gt=time_border).values_list('voting_end_at', flat=True)
    return [time.mktime(accepted_time.timetuple()) for accepted_time in bills_ends]


def initiate_actual_bills_update(account_id):
    amqp_environment.environment.workers.accounts_manager.cmd_run_account_method(account_id=account_id,
                                                                                 method_name=accounts_prototypes.AccountPrototype.update_actual_bills.__name__,
                                                                                 data={})


def update_actual_bills_for_all_accounts():
    for account_id in models.Bill.objects.filter(state=relations.BILL_STATE.ACCEPTED).order_by('owner_id').values_list('owner_id', flat=True).distinct():
        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)
        account.update_actual_bills()
        account.save()
