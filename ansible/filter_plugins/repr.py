
class FilterModule(object):

    def filters(self):
        return {'repr': self.repr}

    def repr(self, value):
        return repr(value)
