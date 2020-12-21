
import dataclasses
import datetime

from . import relations


@dataclasses.dataclass(frozen=True)
class Token:
    __slots__ = ('value', 'account_id', 'expire_at')

    value: str
    account_id: int
    expire_at: datetime.datetime

    def is_expired(self, expiration_delta):
        return self.expire_at < datetime.datetime.now() + datetime.timedelta(seconds=expiration_delta)


@dataclasses.dataclass(frozen=True)
class AccountInfo:
    __slots__ = ('id', 'name', 'email', 'return_url', 'state')

    id: int
    name: str
    email: str
    return_url: str
    state: relations.ACCOUNT_INFO_STATE

    def remove_private_data(self):
        return dataclasses.replace(self,
                                   name=None,
                                   email=None,
                                   state=relations.ACCOUNT_INFO_STATE.REMOVED_BY_GDPR)

    def is_removed_by_gdpr(self):
        return self.state == relations.ACCOUNT_INFO_STATE.REMOVED_BY_GDPR

    def fingerprint(self):
        return (self.id, self.name, self.email, self.return_url, self.state)

    def is_changed(self, other):
        return self.fingerprint() != other.fingerprint()

    def data(self):
        return {'name': self.name,
                'email': self.email}


@dataclasses.dataclass(frozen=True)
class Invoice:
    __slots__ = ('xsolla_id', 'account_id', 'purchased_amount', 'is_test', 'is_fake')

    xsolla_id: int
    account_id: int
    purchased_amount: int
    is_test: bool
    is_fake: bool

    def data(self):
        return {'xsolla_id': self.xsolla_id,
                'purchased_amount': self.purchased_amount}


@dataclasses.dataclass(frozen=True)
class Cancellation:
    __slots__ = ('xsolla_id', 'account_id')

    xsolla_id: int
    account_id: int

    def data(self):
        return {'xsolla_id': self.xsolla_id}
