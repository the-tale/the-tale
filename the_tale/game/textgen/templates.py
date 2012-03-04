# coding: utf-8
import re
import numbers
import random

from dext.utils import s11n

from .models import Word
from .models import Template as TemplateModel
from .exceptions import TextgenException
from .words import Args, WordBase, Numeral
    
class Dictionary(object):

    def __init__(self):
        self.data = {}

    def add_word(self, word):
        self.data[word.normalized] = word

    def get_word(self, normalized):
        return self.data[normalized]

    def save(self):
        for norm, word in self.data.items():
            Word.objects.filter(normalized=norm).delete()
            word.save_to_model()

    def load(self):
        for model in Word.objects.all():
            word = WordBase.create_from_model(model)
            self.add_word(word)


class Vocabulary(object):

    def __init__(self):
        self.data = {}

    def add_phrase(self, type_, template):
        if type_ not in self.data:
            self.data[type_] = []
        self.data[type_].append(template)

    def get_random_phrase(self, type_):
        return random.choice(self.data[type_])

    def save(self):
        for type_, phrases in self.data.items():
            for phrase in phrases:
                phrase.save(type_)

    def load(self):
        for model in TemplateModel.objects.all():
            phrase = Template.create_from_model(model)
            self.add_phrase(model.type, phrase)


class Template(object):

    # [[external_id|dependece|dependece|arguments]]
    EXTERNAL_REGEX = re.compile(u'\[\[[^\]]+\]\]', re.UNICODE)

    # [{internal_id|dependece|dependece|arguments}]
    INTERNAL_REGEX = re.compile(u'\[\{[^\]]+\}\]', re.UNICODE)

    def __init__(self, template, externals, internals):
        self.template = template
        self.externals = externals
        self.internals = internals

    @classmethod
    def prepair_words(cls, morph, regex, src, subsitute_pattern, is_internal):
        words = []
        word_macroses = regex.findall(src)

        for i, word_macros in enumerate(word_macroses):
            slugs = word_macros[2:-2].split('|')

            id_ = slugs[0]
            args = slugs[-1]
            dependences = slugs[1:-1]

            if dependences == ['']: dependences = ()

            str_id = subsitute_pattern % i
            src = src.replace(word_macros, '%%(%s)s' % str_id)
            
            if is_internal:
                normalized = morph.normalize(id_.upper())

                if len(normalized) != 1:
                    raise TextgenException(u'can not determine type of word: %s' % src)

                normalized = list(normalized)[0].lower()
            else:
                normalized = id_


            words.append((normalized, dependences, str_id, tuple(args.split(u','))))

        return src, words


    @classmethod
    def create(cls, morph, src):
        internals = []

        src, externals = cls.prepair_words(morph, cls.EXTERNAL_REGEX, src, 'e_%d', False)
        src, internals = cls.prepair_words(morph, cls.INTERNAL_REGEX, src, 'i_%d', True)

        return cls(src, externals, internals)


    def _preprocess_externals(self, dictionary, externals):
        processed_externals = {}

        for external_id, external in externals.items():
            additional_args = ()
            if isinstance(external, tuple):
                normalized, additional_args = external
                additional_args = additional_args.split(u',')
            else:
                normalized = external

            if isinstance(normalized, numbers.Number):
                word = Numeral(normalized)
                arguments = Args()
            else:
                word = dictionary.get_word(normalized)
                arguments = Args(*word.properties)    

            arguments.update(*additional_args)
            
            processed_externals[external_id] = (word, arguments)

        return processed_externals

    def _create_substitution(self, word, arguments, dependences, externals, args):
        number = None

        for dependence in dependences:
            dependence_word, dependence_args = externals[dependence]
            if isinstance(dependence_word, Numeral):
                number = dependence_word
            else:
                word.update_args(arguments, dependence_word, dependence_args)

        arguments.update(*args)

        if number is not None:
            word.update_args(arguments, number, arguments.get_copy())

        return word.get_form(arguments)


    def substitute(self, dictionary, externals):

        substitutions = {}
        processed_externals = self._preprocess_externals(dictionary, externals)
            
        for external_id, dependences, str_id, args in self.externals:
            word, arguments = processed_externals[external_id]
            substitutions[str_id] = self._create_substitution(word, arguments.get_copy(), dependences, processed_externals, args)

        for internal_str, dependences, str_id, args in self.internals:
            word = dictionary.get_word(internal_str)
            substitutions[str_id] = self._create_substitution(word, Args(), dependences, processed_externals, args)


        return self.template % substitutions


    def save(self, type_):
        data = {'template': self.template,
                'internals': self.internals,
                'externals': self.externals}
        TemplateModel.objects.create(type=type_,
                                     data=s11n.to_json(data))

    @classmethod
    def create_from_model(cls, model):
        data = s11n.from_json(model.data)
        return cls(data['template'], data['externals'], data['internals'])
