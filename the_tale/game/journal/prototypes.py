# coding: utf-8

from .models import Phrase

from .template import Template


class PhrasePrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def type(self): return self.model.type

    @property
    def template(self): 
        if not hasattr(self, '_template'):
            self._template = Template(self.model.template)
        return self._template

    @classmethod
    def get_random(cls, type_):
        return cls(Phrase.objects.filter(type=type_).order_by('?')[0])

    def substitute(self, **kwargs):
        return self.template.substitute(**kwargs)

