
import smart_imports

smart_imports.all()


class Client:
    __slots__ = ('entry_point',)

    def __init__(self, entry_point):
        self.entry_point = entry_point

    def url(self, path):
        return self.entry_point + path
