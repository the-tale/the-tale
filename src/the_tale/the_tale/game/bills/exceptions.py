
import smart_imports

smart_imports.all()


class BillError(utils_exceptions.TheTaleError):
    pass


class UnknownLastEventTextError(BillError):
    MSG = 'unknown last event text for bill %(bill_id)d'


class ApplyBillInWrongStateError(BillError):
    MSG = 'trying to apply bill %(bill_id)d not in voting state'


class StopBillInWrongStateError(BillError):
    MSG = 'trying to stop bill %(bill_id)d not in voting state'


class ApplyUnapprovedBillError(BillError):
    MSG = 'trying to apply bill %(bill_id)d which did not approved by moderator'


class ApplyBillBeforeVoteWasEndedError(BillError):
    MSG = 'trying to apply bill %(bill_id)d before voting period was end'


class EndBillInWrongStateError(BillError):
    MSG = 'trying to end bill %(bill_id)d not in accepted state'


class EndBillAlreadyEndedError(BillError):
    MSG = 'trying to end bill %(bill_id)d which already ended'


class EndBillBeforeTimeError(BillError):
    MSG = "trying to end bill %(bill_id)d before it's timeout"


class DeclinedBillInWrongStateError(BillError):
    MSG = 'trying to decline bill %(bill_id)d in not accepted state'
