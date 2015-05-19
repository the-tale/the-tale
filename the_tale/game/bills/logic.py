# coding: utf-8
import time
import datetime

from the_tale.game.bills import models
from the_tale.game.bills import relations
from the_tale.game.bills import conf


def actual_bills_accepted_timestamps(account_id):
    time_border = datetime.datetime.now() - datetime.timedelta(seconds=conf.bills_settings.BILL_ACTUAL_LIVE_TIME)
    bills_ends =  models.Bill.objects.filter(state=relations.BILL_STATE.ACCEPTED,
                                             ownder=account_id,
                                             voting_end_at__gt=time_border).values_list('voting_end_at', flat=True)
    return [time.mktime(accepted_time.timetuple()) for accepted_time in bills_ends]
