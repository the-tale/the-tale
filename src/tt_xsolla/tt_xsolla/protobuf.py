
from . import objects
from . import relations


def to_account_info(account_info):
    return objects.AccountInfo(id=account_info.id,
                               name=account_info.name,
                               email=account_info.email,
                               return_url=account_info.return_url,
                               state=relations.ACCOUNT_INFO_STATE.ACTIVE)
