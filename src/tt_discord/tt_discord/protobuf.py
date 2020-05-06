import time

from tt_protocol.protocol import discord_pb2


def from_bind_code(code):
    return discord_pb2.BindCode(code=code.code.hex,
                                created_at=time.mktime(code.created_at.timetuple()) + code.created_at.microsecond / 1000000,
                                expire_at=time.mktime(code.expire_at.timetuple()) + code.expire_at.microsecond / 1000000)
