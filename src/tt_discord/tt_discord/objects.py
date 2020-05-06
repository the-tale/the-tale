
import uuid
import datetime
import dataclasses


@dataclasses.dataclass(frozen=True)
class BindCode:
    __slots__ = ('code', 'created_at', 'expire_at')

    code: uuid.UUID
    created_at: datetime.datetime
    expire_at: datetime.datetime

    def is_expired(self):
        return self.expire_at < datetime.datetime.now(datetime.timezone.utc)


@dataclasses.dataclass(frozen=True)
class AccountInfo:
    __slots__ = ('id', 'game_id', 'discord_id')

    id: int
    game_id: int
    discord_id: int

    def is_binded(self):
        return None not in (self.id, self.game_id, self.discord_id)
