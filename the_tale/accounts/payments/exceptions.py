# coding: utf-8

from common.utils.exceptions import TheTaleError

class PaymentsError(TheTaleError): pass

class FastAccountError(PaymentsError):
    MSG = 'try to buy purchase %(purchase_uid)s to fast account %(account_id)s'

class DuplicateUIDsInPriceListError(PaymentsError):
    MSG = 'duplicate uids in price list'

class DuplicatePermanentPurchaseError(PaymentsError):
    MSG = 'try to buy duplicate permanent purchase %(purchase_id)s of type %(purchase_type)r for account %(account_id)s'
