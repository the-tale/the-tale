
import typing
import datetime
import dataclasses


@dataclasses.dataclass
class Message:
    __slots__ = ('id', 'sender', 'recipients', 'created_at', 'body', 'visible')

    id: int
    sender: int
    recipients: typing.List[int]
    created_at: datetime.datetime
    body: str
    visible: bool

    def data_of(self, account_id):
        return {'id': self.id,
                'sender': self.sender,
                'recipients': self.recipients if account_id == self.sender else [account_id],
                'created_at': self.created_at.isoformat(),
                'text': self.body,
                'removed': not self.visible}
