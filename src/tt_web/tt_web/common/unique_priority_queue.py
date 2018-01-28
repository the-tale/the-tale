
import heapq


class Queue(object):
    __slots__ = ('_heap', '_set')

    def __init__(self):
        self._heap = []
        self._set = {}

    def empty(self):
        return not self._set

    def push(self, id, value):
        # do not add to queue not changed items
        if id in self._set and self._set[id] == value:
            return

        # not remove old item if add to query changed item
        # it will be filtered in pop or first
        self._set[id] = value
        heapq.heappush(self._heap, (value, id))

    def pop(self):
        while self._heap:
            value, id = heapq.heappop(self._heap)

            if self._set[id] == value:
                del self._set[id]
                return id, value

        return None, None

    def first(self):
        while self._heap:
            value, id = self._heap[0]

            if self._set[id] == value:
                return id, value
            else:
                heapq.heappop(self._heap)

        return None, None

    def items(self):
        while not self.empty():
            yield self.pop()

    def clean(self):
        self._heap = []
        self._set = {}

    def __len__(self):
        return len(self._set)
