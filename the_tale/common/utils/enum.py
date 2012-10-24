# coding: utf-8

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

        def __init__(self, value):
            self.value = value

        def update(self, value):
            self.value = value.value if isinstance(value, self.__class__) else value

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

        setattr(Enum, 'is_%s' % field_name.lower(), property(_create_state_checker(field_id)))

    Enum.__name__ = class_name

    return Enum
