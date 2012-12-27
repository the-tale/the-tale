# coding: utf-8

class EnumException(Exception): pass

def _create_state_checker(value):
    return lambda self: self.value == value

def create_enum(class_name, records):
    '''
    records is [(field_name, feild_id, help_text), ...]

    cls._CHOICES - django choices
    cls._ID_TO_STR - {field_id: field_name}
    cls._STR_TO_ID - {field_name: field_id}
    cls.<field_name> = field_id
    cls(id) - construct object to perform checks
    obj.is_<field_name> - True if state in filed_name state
    '''

    class Enum(object):
        _CHOICES = []
        _ID_TO_STR = {}
        _STR_TO_ID = {}
        _ID_TO_TEXT = {}
        _ALL = []

        def __init__(self, value):
            self.value = value
            self.verbose = self._ID_TO_TEXT[value]

        def update(self, value):
            value = value.value if isinstance(value, self.__class__) else value
            if value not in self._ALL:
                raise EnumException('try to set wrong value <%r> for enum %r' % (value, self))
            self.value = value


        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.value == other.value
            return self.value == other

    for field_name, field_id, help_text in records:
        setattr(Enum, field_name, field_id)
        Enum._CHOICES.append((field_id, help_text))
        Enum._STR_TO_ID[field_name] = field_id
        Enum._ID_TO_STR[field_id] = field_name
        Enum._ID_TO_TEXT[field_id] = help_text
        Enum._ALL.append(field_id)

        setattr(Enum, 'is_%s' % field_name.lower(), property(_create_state_checker(field_id)))

    if len(records) != len(Enum._STR_TO_ID):
        raise Exception('enum "%s" has duplicate field names' % class_name)

    if len(records) != len(Enum._ID_TO_STR):
        raise Exception('enum "%s" has duplicate field ids' % class_name)

    Enum.__name__ = class_name

    return Enum
