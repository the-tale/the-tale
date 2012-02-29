# coding: utf-8

from .models import Word, WORD_TYPE, PROPERTIES
from .exceptions import TextgenException


class WordBase(object):

    TYPE = None
    
    def __init__(self, forms, properties):
        self.forms = tuple(forms)
        self.properties = tuple(properties)

    @property
    def normalized(self): return self.forms[0]

    def get_form(self, args):
        raise NotImplemented

    @classmethod
    def create_from_baseword(cls, src):
        raise NotImplemented
    
    @classmethod
    def create_from_model(cls, model):
        return cls(forms=model.forms.split('|'),
                   properties=model.properties.split('|'))

    def save_to_model(self):
        Word.objects.filter(normalized=self.normalized).delete()
        return Word.objects.create(normalized=self.normalized,
                                   type=self.TYPE,
                                   forms='|'.join(self.forms),
                                   properties='|'.join(self.properties))


class Noun(WordBase):

    TYPE = WORD_TYPE.NOUN

    @property
    def gender(self): return self.properties[0]

    def get_form(self, args):
        return self.forms[PROPERTIES.NUMBERS.index(args.number) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]

    def pluralize(self, number, case):
        raise NotImplemented

    @classmethod
    def create_from_baseword(cls, morph, src):
        normalized = morph.normalize(src.upper())

        if len(normalized) != 1:
            raise TextgenException(u'can not determine type of word: %s' % src)

        normalized = list(normalized)[0]

        forms = []

        for number in PROPERTIES.NUMBERS:
            for case in PROPERTIES.CASES:
                # print number, case, morph.inflect_ru(normalized, '%s,%s' % (case, number) ).lower()
                forms.append(morph.inflect_ru(normalized, '%s,%s' % (case, number) ).lower() )

        gram_info = morph.get_graminfo(normalized)[0]

        info = gram_info['info']

        if u'мр' in info:
            properties = [u'мр']
        elif u'ср' in info:
            properties = [u'ср']
        else:
            properties = [u'жр']

        return cls(forms=forms, properties=properties)
