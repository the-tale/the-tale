

class Result:
    __init__ = ()

    def is_error(self, name=None):
        raise NotImplementedError()

    def is_ok(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __neq__(self, other):
        return not self.__eq__(other)


class Ok(Result):
    __init__ = ('value',)

    def __init__(self, value=True):
        self.value = value

    def is_error(self, name=None):
        return False

    def is_ok(self):
        return True

    def __str__(self):
        return f"Ok({self.value}))"

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.value == other.value)


class Error(Result):
    __init__ = ('name', 'data')

    is_error = True

    def __init__(self, name, data=None):
        self.name = name
        self.data = data

    def is_error(self, name=None):
        if name is None:
            return True

        return self.name == name

    def is_ok(self):
        return False

    def __str__(self):
        return f"Error('{self.name}', {self.data})"

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.name == other.name and
                self.data == other.data)
