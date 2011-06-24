# -*- coding: utf-8 -*-

from .prototypes import JournalMessageException

def get_renderers_types():
    renderers = {}
    for key, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, MessageRendererBase) and cls != MessageRendererBase:
            renderers[cls.TYPE] = cls
    return renderers

  

class MessageRendererBase(object):

    TYPE = 'BASE'
    NAME = 'base'

    def __init__(self):
        pass

    def render(self, *argv, **kwargs):
        raise JournalMessageException('class %s does not define render(...) method' % str(self.__class__))


class ActionIdlenessMessage(MessageRendererBase):
    
    TYPE = 'ACTION_IDLENESS'
    NAME = 'message for idleness action'

    def render(self, pattern):
        return pattern.text


class PushToActionMessage(MessageRendererBase):
    
    TYPE = 'CARD_PUSH_TO_ACTION'
    NAME = 'message for "push to action" card usage'

    def render(self, pattern):
        return pattern.text


RENDERERS = get_renderers_types()
RENDERERS_CHOICES = [ (renderer.TYPE, renderer.NAME) for renderer in RENDERERS.values()]
