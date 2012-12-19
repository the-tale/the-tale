# coding: utf-8

class EnumException(Exception): pass

def _create_state_checker(value):
    return lambda self: self.value == value

def create_enum(class_name, records):
    '''
    records is [(field_name, feild_id, help_text), ...]

    cls.CHOICES - django choices
    cls.ID_2_STR - {field_id: field_name}
    cls.STR_2_ID - {field_name: field_id}
    cls.<field_name> = field_id
    cls(id) - construct object to perform checks
    obj.is_<field_name> - True if state if filed_name state
    '''

    class Enum(object):
        CHOICES = []
        ID_2_STR = {}
        STR_2_ID = {}
        ID_2_TEXT = {}
        ALL = []

        def __init__(self, value):
            self.value = value
            self.verbose = self.ID_2_TEXT[value]

        def update(self, value):
            value = value.value if isinstance(value, self.__class__) else value
            if value not in self.ALL:
                raise EnumException('try to set wrong value <%r> for enum %r' % (value, self))
            self.value = value


        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.value == other.value
            return self.value == other

    for field_name, field_id, help_text in records:
        setattr(Enum, field_name, field_id)
        Enum.CHOICES.append((field_id, help_text))
        Enum.STR_2_ID[field_name] = field_id
        Enum.ID_2_STR[field_id] = field_name
        Enum.ID_2_TEXT[field_id] = help_text
        Enum.ALL.append(field_id)

        setattr(Enum, 'is_%s' % field_name.lower(), property(_create_state_checker(field_id)))

    if len(records) != len(Enum.STR_2_ID):
        raise Exception('enum "%s" has duplicate field names' % class_name)

    if len(records) != len(Enum.ID_2_STR):
        raise Exception('enum "%s" has duplicate field ids' % class_name)

    Enum.__name__ = class_name

    return Enum
