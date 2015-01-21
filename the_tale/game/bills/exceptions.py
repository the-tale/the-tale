# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class BillError(TheTaleError): pass

class UnknownLastEventTextError(BillError):
    MSG = u'unknown last event text for bill %(bill_id)d'

class ApplyBillInWrongStateError(BillError):
    MSG = u'trying to apply bill %(bill_id)d not in voting state'

class ApplyUnapprovedBillError(BillError):
    MSG = u'trying to apply bill %(bill_id)d which did not approved by moderator'

class ApplyBillBeforeVoteWasEndedError(BillError):
    MSG = u'trying to apply bill %(bill_id)d before voting period was end'


class EndBillInWrongStateError(BillError):
    MSG = u'trying to end bill %(bill_id)d not in accepted state'

class EndBillAlreadyEndedError(BillError):
    MSG = u'trying to end bill %(bill_id)d which already ended'

class EndBillBeforeTimeError(BillError):
    MSG = u"trying to end bill %(bill_id)d before it's timeout"


class DeclinedBillInWrongStateError(BillError):
    MSG = u'trying to decline bill %(bill_id)d in not accepted state'
