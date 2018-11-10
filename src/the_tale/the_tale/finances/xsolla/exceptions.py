
import smart_imports

smart_imports.all()


class XsollaError(utils_exceptions.TheTaleError):
    pass


class WrongInvoiceStateInProcessingError(XsollaError):
    MSG = 'invoice %(invoice_id)d: wrong invoice_state: "%(state)s"'
