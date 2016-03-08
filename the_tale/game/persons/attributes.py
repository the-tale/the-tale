# coding: utf-8

from the_tale.game.balance import constants as c
from the_tale.game import attributes

from . import relations


class Attributes(attributes.create_attributes_class(relations.ATTRIBUTE)):
    __slots__ = ()
