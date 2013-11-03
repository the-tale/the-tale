# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class XsollaError(TheTaleError): pass

class WrongInvoiceStateInProcessingError(XsollaError):
    MSG = u'invoice %(invoice_id)d: wrong invoice_state: "%(state)s"'
