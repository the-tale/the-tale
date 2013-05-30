# coding: utf-8

from common.utils.exceptions import TheTaleError

class DengionlineError(TheTaleError): pass

class WrongOrderIdInConfirmationError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: wrong order_id: "%(order_id)s"'

class WrongUserIdInConfirmationError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: wrong user_id: "%(user_id)s"'

class WrongRequestKeyInConfirmationError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: wrong key: "%(key)s"'

class InvoiceAlreadyConfirmedError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: already confirmed"'
