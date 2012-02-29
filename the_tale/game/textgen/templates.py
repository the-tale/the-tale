# coding: utf-8
import re

from .models import PROPERTIES
from .exceptions import TextgenException

class Args(object):

    __slots__ = ('case', 'number')

    def __init__(self, *args):
        self.case = u'им'
        self.number = u'ед'
        self.update(*args)

    def update(self, *args):
        for arg in args:
            if arg in PROPERTIES.CASES:
                self.case = arg
            elif arg in PROPERTIES.NUMBERS:
                self.number = arg

    
class Dictionary(object):

    def __init__(self):
        self.data = {}

    def add_word(self, word):
        self.data[word.normalized] = word

    def get_word(self, normalized):
        return self.data[normalized]


class Template(object):

    EXTERNAL_REGEX = re.compile(u'\[\[[^\]]+\|[^\]]+\]\]', re.UNICODE)
    INTERNAL_REGEX = re.compile(u'\[\{[^\]]+\|[^\]]+\}\]', re.UNICODE)

    def __init__(self, template, externals, internals):
        self.template = template
        self.externals = externals
        self.internals = internals


    @classmethod
    def create(cls, morph, src):
        external_macroses = cls.EXTERNAL_REGEX.findall(src)
        externals = []
        internals = []
        
        for i, external_macros in enumerate(external_macroses):
            external_id, args = external_macros[2:-2].split('|')
            str_id = 'e_%d' % i
            src = src.replace(external_macros, '%%(%s)s' % str_id)
            externals.append((external_id, str_id, tuple(args.split(u','))))

        internal_macroses = cls.INTERNAL_REGEX.findall(src)

        for i, internal_macros in enumerate(internal_macroses):
            data = internal_macros[2:-2].split('|')
            
            if len(data) == 2:
                internal_str, external_id = data
                args = ()
            else:
                internal_str, external_id, args = data
                args = tuple(args.split(u','))

            str_id = 'i_%d' % i
            src = src.replace(internal_macros, '%%(%s)s' % str_id)

            normalized = morph.normalize(internal_str.upper())

            if len(normalized) != 1:
                raise TextgenException(u'can not determine type of word: %s' % src)

            normalized = list(normalized)[0].lower()

            internals.append((normalized, external_id, str_id, args))

        return cls(src, externals, internals)


    def substitute(self, dictionary, externals):

        data = {}
        
        for external_id, str_id, args in self.externals:
            arguments = args

            external = externals[external_id]

            if isinstance(external, tuple):
                normalized, additional_args = external
                if additional_args:
                    arguments += tuple(additional_args.split(u','))
            else:
                normalized = external
                
            arguments = Args(*arguments)

            data[str_id] = dictionary.get_word(normalized).get_form(arguments)

            
        # TODO: remove copy-past parts
        for internal_str, external_id, str_id, args in self.internals:
            arguments = args
            
            external = externals[external_id]

            if isinstance(external, tuple):
                normalized, additional_args = external
                if additional_args:
                    arguments += tuple(additional_args.split(u','))
            # else:
            #     normalized = external

            arguments = Args(*arguments)

            data[str_id] = dictionary.get_word(internal_str).get_form(arguments)


        return self.template % data

    @classmethod
    def from_source(cls, src):
        pass
