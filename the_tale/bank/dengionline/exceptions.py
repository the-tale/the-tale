# coding: utf-8

from common.utils.exceptions import TheTaleError

class DengionlineError(TheTaleError): pass

class WrongInvoiceStateInConfirmationError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: wrong invoice_state: "%(state)s"'

class WrongInvoiceStateInProcessingError(DengionlineError):
    MSG = u'invoice %(invoice_id)d: wrong invoice_state: "%(state)s"'

class CreationLimitError(DengionlineError):
    MSG = u'account %(account_id)s made too many invoice requests'

class WrongValueTypeError(DengionlineError):
    MSG = u'unexpected type of value %(value_name)s: %(type)s'
