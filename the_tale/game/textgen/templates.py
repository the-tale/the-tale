# coding: utf-8
import re
#import numbers

from .exceptions import TextgenException
from .words import Args
    
class Dictionary(object):

    def __init__(self):
        self.data = {}

    def add_word(self, word):
        self.data[word.normalized] = word

    def get_word(self, normalized):
        return self.data[normalized]


class Template(object):

    # [[external_id|arguments]]
    EXTERNAL_REGEX = re.compile(u'\[\[[^\]]+\]\]', re.UNICODE)

    # [{internal_id|external_id|arguments}]
    INTERNAL_REGEX = re.compile(u'\[\{[^\]]+\}\]', re.UNICODE)

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
            external_arguments = external_macros[2:-2].split('|')

            external_id = external_arguments[0]
            args = external_arguments[-1]
            dependences = external_arguments[1:-1]

            str_id = 'e_%d' % i
            src = src.replace(external_macros, '%%(%s)s' % str_id)

            externals.append((external_id, dependences, str_id, tuple(args.split(u','))))

        internal_macroses = cls.INTERNAL_REGEX.findall(src)

        for i, internal_macros in enumerate(internal_macroses):
            internal_arguments = internal_macros[2:-2].split('|')

            internal_str = internal_arguments[0]
            args = internal_arguments[-1]
            dependences = internal_arguments[1:-1]

            str_id = 'i_%d' % i
            src = src.replace(internal_macros, '%%(%s)s' % str_id)

            normalized = morph.normalize(internal_str.upper())

            if len(normalized) != 1:
                raise TextgenException(u'can not determine type of word: %s' % src)

            normalized = list(normalized)[0].lower()

            internals.append((normalized, dependences, str_id, tuple(args.split(u','))))

        return cls(src, externals, internals)


    def substitute(self, dictionary, externals):

        substitutions = {}
        processed_externals = {}

        for external_id, external in externals.items():
            additional_args = ()
            if isinstance(external, tuple):
                normalized, additional_args = external
                additional_args = additional_args.split(u',')
            else:
                normalized = external

            word = dictionary.get_word(normalized)

            arguments = Args(*word.properties)    
            arguments.update(*additional_args)
            
            processed_externals[external_id] = (word, arguments)

            
        for external_id, dependences, str_id, args in self.externals:

            word, arguments = processed_externals[external_id]

            arguments = arguments.get_copy()

            for dependence in dependences:
                dependence_word, dependence_args = processed_externals[dependence]
                word.update_args(arguments, dependence_word.__class__, dependence_args)

            arguments.update(*args)

            substitutions[str_id] = word.get_form(arguments)

        # TODO: remove copy-past parts
        for internal_str, dependences, str_id, args in self.internals:

            word = dictionary.get_word(internal_str)

            arguments = Args()

            for dependence in dependences:
                dependence_word, dependence_args = processed_externals[dependence]
                word.update_args(arguments, dependence_word.__class__, dependence_args)

            arguments.update(*args)
            

            substitutions[str_id] = word.get_form(arguments)


        return self.template % substitutions

    @classmethod
    def from_source(cls, src):
        pass
