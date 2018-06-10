
from the_tale.game import attributes

from . import relations


class Attributes(attributes.create_attributes_class(relations.ATTRIBUTE)):
    __slots__ = ()
