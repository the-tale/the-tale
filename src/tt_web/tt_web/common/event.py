
import asyncio


_EVENTS = {}


def get(name):
    if name not in _EVENTS:
        _EVENTS[name] = asyncio.Event()

    return _EVENTS[name]


def clear():
    _EVENTS.clear()
