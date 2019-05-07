
import asyncio


_SEMAPHORES = {}


def get(name, value):
    if name not in _SEMAPHORES:
        _SEMAPHORES[name] = asyncio.Semaphore(value)

    return _SEMAPHORES[name]


def clear():
    _SEMAPHORES.clear()
